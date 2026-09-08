"""Payable vouchers and their receipt or purchase-return sources."""

from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .base import ApprovalStatus, AuditedModel


class PayableVoucher(AuditedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    voucher_date = models.DateField(default=timezone.localdate)
    supplier = models.ForeignKey("Partner", on_delete=models.PROTECT, related_name="payable_vouchers")
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="payable_vouchers")
    payment_method = models.CharField(max_length=80)
    due_date = models.DateField(null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(Decimal("0"))])
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    invoice_number = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=240, blank=True)
    source_object = models.CharField(max_length=40, default="ap_mstr")

    class Meta:
        ordering = ("-voucher_date", "-number")

    def recalculate(self):
        totals = self.lines.aggregate(
            net=models.Sum("net_amount"),
            tax=models.Sum("tax_amount"),
            gross=models.Sum("gross_amount"),
        )
        self.net_amount = totals["net"] or Decimal("0")
        self.tax_amount = totals["tax"] or Decimal("0")
        self.gross_amount = totals["gross"] or Decimal("0")
        self.save(update_fields=["net_amount", "tax_amount", "gross_amount", "updated_at"])

    def approve(self, actor):
        if not self.lines.exists():
            raise ValidationError("应付凭单至少需要一条来源明细")
        super().approve(actor)

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"AP-{timezone.now():%Y%m%d%H%M%S%f}"
        super().save(*args, **kwargs)


class PayableVoucherLine(models.Model):
    voucher = models.ForeignKey(PayableVoucher, on_delete=models.CASCADE, related_name="lines")
    line_number = models.PositiveIntegerField()
    source_receipt_line = models.OneToOneField(
        "GoodsReceiptLine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payable_voucher_line",
    )
    source_purchase_return_line = models.OneToOneField(
        "PurchaseReturnLine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payable_voucher_line",
    )
    material = models.ForeignKey("Material", on_delete=models.PROTECT, related_name="payable_voucher_lines")
    uom = models.ForeignKey("Uom", on_delete=models.PROTECT, related_name="payable_voucher_lines")
    quantity = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0.000001"))])
    unit_price = models.DecimalField(max_digits=18, decimal_places=6, validators=[MinValueValidator(Decimal("0"))])
    net_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0"), editable=False)
    source_object = models.CharField(max_length=40, default="apd_det")

    class Meta:
        ordering = ("voucher", "line_number")
        constraints = [
            models.UniqueConstraint(fields=("voucher", "line_number"), name="uniq_payable_voucher_line"),
            models.CheckConstraint(
                condition=(
                    models.Q(source_receipt_line__isnull=False, source_purchase_return_line__isnull=True)
                    | models.Q(source_receipt_line__isnull=True, source_purchase_return_line__isnull=False)
                ),
                name="payable_line_exactly_one_source",
            ),
        ]

    def clean(self):
        if bool(self.source_receipt_line_id) == bool(self.source_purchase_return_line_id):
            raise ValidationError("应付来源必须且只能选择收货明细或采购退货明细")
        source = self.source_receipt_line if self.source_receipt_line_id else self.source_purchase_return_line
        order_line = source.purchase_order_line
        document = source.receipt if self.source_receipt_line_id else source.purchase_return
        if document.status != ApprovalStatus.APPROVED:
            raise ValidationError("只有已审核收货或采购退货明细可以生成应付凭单")
        if self.voucher_id and (
            self.voucher.supplier_id != document.supplier_id
            or self.voucher.currency_id != order_line.order.currency_id
            or self.voucher.payment_method != order_line.order.payment_method
            or self.voucher.tax_rate != order_line.order.tax_rate
        ):
            raise ValidationError("应付凭单供应商、币种、支付方式和税率必须与来源采购单一致")
        if self.material_id != source.material_id or self.uom_id != source.uom_id:
            raise ValidationError("应付凭单物料和单位必须与收货明细一致")
        if self.quantity != source.quantity:
            raise ValidationError({"quantity": "应付数量必须与来源明细一致"})
        if self.unit_price != order_line.unit_price:
            raise ValidationError({"unit_price": "应付单价必须与来源采购行一致"})

    def save(self, *args, **kwargs):
        sign = Decimal("1") if self.source_receipt_line_id else Decimal("-1")
        self.net_amount = (sign * self.quantity * self.unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.tax_amount = (self.net_amount * self.voucher.tax_rate / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        self.gross_amount = self.net_amount + self.tax_amount
        super().save(*args, **kwargs)
        self.voucher.recalculate()
