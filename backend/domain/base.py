"""Base domain models; Django app label remains backend."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ApprovalStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    PENDING = "pending", "待审核"
    APPROVED = "approved", "已审核"
    REJECTED = "rejected", "已驳回"
    VOID = "void", "已作废"


class AuditedModel(models.Model):
    status = models.CharField(max_length=16, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    created_by = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.CharField(max_length=64, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=240, blank=True)
    is_confirmed = models.BooleanField(default=False)
    confirmed_by = models.CharField(max_length=64, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def submit(self):
        if self.status not in {ApprovalStatus.DRAFT, ApprovalStatus.REJECTED}:
            raise ValidationError("只有草稿或已驳回记录可以提交审核")
        self.status = ApprovalStatus.PENDING

    def approve(self, actor):
        if self.status != ApprovalStatus.PENDING:
            raise ValidationError("只有待审核记录可以审核")
        self.status = ApprovalStatus.APPROVED
        self.approved_by = actor
        self.approved_at = timezone.now()
        self.rejection_reason = ""

    def reject(self, actor, reason):
        if self.status != ApprovalStatus.PENDING:
            raise ValidationError("只有待审核记录可以驳回")
        if not reason:
            raise ValidationError("驳回必须填写原因")
        self.status = ApprovalStatus.REJECTED
        self.approved_by = actor
        self.approved_at = timezone.now()
        self.rejection_reason = reason

    def unapprove(self):
        if self.status != ApprovalStatus.APPROVED:
            raise ValidationError("只有已审核记录可以反审核")
        self.status = ApprovalStatus.DRAFT
        self.approved_by = ""
        self.approved_at = None

    def confirm(self, actor):
        if self.status != ApprovalStatus.APPROVED:
            raise ValidationError("只有已审核记录可以确认")
        if self.is_confirmed:
            raise ValidationError("记录已经确认")
        self.is_confirmed = True
        self.confirmed_by = actor
        self.confirmed_at = timezone.now()

    def unconfirm(self):
        if not self.is_confirmed:
            raise ValidationError("记录尚未确认")
        self.is_confirmed = False
        self.confirmed_by = ""
        self.confirmed_at = None

    def void(self):
        if self.status == ApprovalStatus.VOID:
            raise ValidationError("记录已经作废")
        self.status = ApprovalStatus.VOID

    def restore(self):
        if self.status != ApprovalStatus.VOID:
            raise ValidationError("只有已作废记录可以反作废")
        self.status = ApprovalStatus.DRAFT
        self.is_confirmed = False
        self.confirmed_by = ""
        self.confirmed_at = None


class DocumentEvidence(models.Model):
    """Signed slips and other evidence linked to an ERP document."""

    class EvidenceType(models.TextChoices):
        SUPPLIER_DELIVERY = "supplier_delivery", "供应商送货签收单"
        CUSTOMER_DELIVERY = "customer_delivery", "客户送货签收单"
        CUSTOMER_RETURN = "customer_return", "客户退货单"
        WAREHOUSE_RETURN = "warehouse_return", "仓库退货单"

    document_type = models.CharField(max_length=40)
    document_id = models.PositiveIntegerField()
    document_number = models.CharField(max_length=80, blank=True)
    evidence_type = models.CharField(max_length=32, choices=EvidenceType.choices)
    file = models.FileField(upload_to="document_evidence/")
    notes = models.CharField(max_length=240, blank=True)
    uploaded_by = models.CharField(max_length=64, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploaded_at", "-id")
        indexes = [models.Index(fields=("document_type", "document_id"), name="evidence_document_idx")]


class AuditEvent(models.Model):
    model = models.CharField(max_length=120)
    object_id = models.CharField(max_length=64)
    action = models.CharField(max_length=40)
    actor = models.CharField(max_length=64)
    reason = models.CharField(max_length=240, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
