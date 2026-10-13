from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from backend.models import (
    AccountingAccount,
    Employee,
    BusinessGroup,
    Company,
    Currency,
    CurrencyRate,
    CustomerAddress,
    Location,
    Material,
    MaterialCompany,
    MaterialUomConversion,
    Partner,
    PartnerBankAccount,
    PartnerCompany,
    PartnerContact,
    PaymentMethod,
    ProductCategory,
    TaxCode,
    Uom,
    UomCategory,
    Warehouse,
)

from .common import BaseSerializer, serializer_for

CompanySerializer = serializer_for(Company)


BusinessGroupSerializer = serializer_for(BusinessGroup)


CurrencySerializer = serializer_for(Currency)


class CurrencyRateSerializer(BaseSerializer):
    class Meta:
        model = CurrencyRate
        fields = '__all__'
        read_only_fields = ('source_object', 'created_by', 'created_at', 'updated_by', 'updated_at')

    def validate(self, attrs):
        from django.db.models import Q
        currency = attrs.get('currency', getattr(self.instance, 'currency', None))
        start = attrs.get('effective_date', getattr(self.instance, 'effective_date', None))
        end = attrs.get('expiry_date', getattr(self.instance, 'expiry_date', None))
        if end and start and end < start:
            raise serializers.ValidationError('汇率失效日期不能早于生效日期')
        if currency and start:
            overlaps = CurrencyRate.objects.filter(currency=currency).exclude(pk=getattr(self.instance, 'pk', None))
            if end:
                overlaps = overlaps.filter(effective_date__lte=end)
            if overlaps.filter(Q(expiry_date__isnull=True) | Q(expiry_date__gte=start)).exists():
                raise serializers.ValidationError('同一币种的汇率有效期间不能重叠')
        return super().validate(attrs)


PaymentMethodSerializer = serializer_for(PaymentMethod)


class CustomerAddressSerializer(BaseSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"
        read_only_fields = (
            "created_by",
            "created_at",
            "updated_by",
            "updated_at",
            "source_object",
            "source_key",
        )


LocationSerializer = serializer_for(Location)


class MaterialSerializer(BaseSerializer):
    category_code = serializers.CharField(source="category.code", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    uom_code = serializers.CharField(source="uom.code", read_only=True)
    uom_name = serializers.CharField(source="uom.name", read_only=True)
    default_location_code = serializers.CharField(source="default_location.code", read_only=True)
    default_location_name = serializers.CharField(source="default_location.name", read_only=True)
    tax_master_code = serializers.CharField(source="tax_master.code", read_only=True, allow_null=True)
    tax_master_name = serializers.CharField(source="tax_master.name", read_only=True, allow_null=True)

    class Meta:
        model = Material
        fields = "__all__"
        read_only_fields = (
            "created_by", "created_at", "updated_by", "updated_at",
            "category_code", "category_name", "uom_code", "uom_name",
            "default_location_code", "default_location_name",
            "tax_master_code", "tax_master_name", "tax_name",
        )
        extra_kwargs = {"tax_code": {"required": False}}

    def validate_tax_master(self, value):
        if value and (not value.active or value.status == "void"):
            raise serializers.ValidationError("税务编码不存在或已停用")
        return value

    def validate(self, attrs):
        tax_master = attrs.get("tax_master", getattr(self.instance, "tax_master", None))
        if tax_master:
            attrs["tax_code"] = tax_master.code
            attrs["tax_name"] = tax_master.name
            if not attrs.get("invoice_name", getattr(self.instance, "invoice_name", "")):
                attrs["invoice_name"] = tax_master.invoice_name
        specification = attrs.get("specification", getattr(self.instance, "specification", ""))
        if not str(specification or "").strip():
            raise serializers.ValidationError({"specification": "规格型号为必填项"})
        return super().validate(attrs)


MaterialCompanySerializer = serializer_for(MaterialCompany)


MaterialUomConversionSerializer = serializer_for(MaterialUomConversion)


class PartnerContactInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerContact
        fields = ("name", "position", "phone", "fax", "email", "is_primary")


class PartnerBankInputSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = PartnerBankAccount
        exclude = ('partner',)
        read_only_fields = ('created_by', 'created_at', 'updated_by', 'updated_at', 'modification_count')

    def validate_account_type(self, value):
        if value not in ('company', 'personal'):
            raise serializers.ValidationError('类型只能为公司或个人')
        return value


class PartnerSerializer(BaseSerializer):
    contacts = PartnerContactInputSerializer(many=True, required=False)
    bank_accounts = PartnerBankInputSerializer(many=True, required=False)
    payment_method_name = serializers.CharField(source="payment_method_master.description", read_only=True)

    class Meta:
        model = Partner
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def validate_copper_currency(self, value):
        if value and not Currency.objects.filter(code=value).exists():
            raise serializers.ValidationError('铜币种必须使用货币资料中的代码')
        return value

    def validate(self, attrs):
        contacts = attrs.pop("contacts", None)
        banks = attrs.pop('bank_accounts', None)
        supplier = attrs.get('kind', getattr(self.instance, 'kind', None)) in ('supplier', 'both')
        if supplier:
            for field, allowed in {'supplier_type': ('1','2','3'), 'quote_method': ('1','2'), 'invoice_type': ('1','2','9'), 'material_price_method': ('01','02','03','04','05','06','07')}.items():
                if attrs.get(field) and attrs[field] not in allowed:
                    raise serializers.ValidationError({field: '请选择有效代码'})
            for field in ('purchase_account', 'temporary_payable_account', 'outsource_fee_account', 'outsource_material_account'):
                if attrs.get(field) and not AccountingAccount.objects.filter(code=attrs[field], active=True).exists():
                    raise serializers.ValidationError({field: '会计科目不存在或已停用'})
            if attrs.get('buyer') and not Employee.objects.filter(code=attrs['buyer']).exists():
                raise serializers.ValidationError({'buyer': '采购员必须关联员工资料代码'})
            for field in ('payment_method_2', 'payment_method_3'):
                if attrs.get(field) and not PaymentMethod.objects.filter(code=attrs[field]).exists():
                    raise serializers.ValidationError({field: '支付方式代码不存在'})
            if attrs.get('quote_method'):
                attrs['quote_tax_included'] = attrs['quote_method'] == '1'
        if banks is not None:
            numbers = [row['line_number'] for row in banks if 'line_number' in row]
            if len(numbers) != len(set(numbers)):
                raise serializers.ValidationError({'bank_accounts': '银行账户行号不能重复'})
            owned = set(self.instance.bank_accounts.values_list('id', flat=True)) if self.instance else set()
            ids = [row['id'] for row in banks if 'id' in row]
            if len(ids) != len(set(ids)) or not set(ids).issubset(owned):
                raise serializers.ValidationError({'bank_accounts': '银行账户不属于当前供应商或存在重复行'})
        master = attrs.get("payment_method_master")
        if master:
            attrs["payment_method"] = master.code
        elif 'payment_method_master' in attrs and not attrs.get('payment_method_master'):
            attrs['payment_method'] = ''
        elif attrs.get("payment_method"):
            attrs["payment_method_master"] = PaymentMethod.objects.filter(code=attrs["payment_method"]).first()
        attrs = super().validate(attrs)
        if contacts is not None and len(contacts) > 4:
            raise serializers.ValidationError({"contacts": "最多可保存 4 个联系方式"})
        attrs["contacts"] = contacts
        attrs['bank_accounts'] = banks
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        contacts = validated_data.pop("contacts", None)
        banks = validated_data.pop('bank_accounts', None)
        partner = Partner.objects.create(**validated_data)
        self._replace_contacts(partner, contacts)
        self._save_banks(partner, banks)
        return partner

    @transaction.atomic
    def update(self, instance, validated_data):
        contacts = validated_data.pop("contacts", None)
        banks = validated_data.pop('bank_accounts', None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.save()
        self._replace_contacts(instance, contacts)
        self._save_banks(instance, banks)
        return instance

    def _save_banks(self, partner, rows):
        if rows is None:
            return
        actor = self.context['request'].user.get_username() if self.context.get('request') else ''
        existing = {row.pk: row for row in partner.bank_accounts.all()}
        keep = []
        for index, data in enumerate(rows, 1):
            pk = data.pop('id', None)
            row = existing.get(pk)
            if row:
                changed = any(getattr(row, key) != value for key, value in data.items())
                if changed:
                    for key, value in data.items():
                        setattr(row, key, value)
                    row.updated_by, row.updated_at = actor, timezone.now()
                    row.modification_count += 1
                    row.save()
            else:
                data.setdefault('line_number', index * 10)
                row = PartnerBankAccount.objects.create(partner=partner, created_by=actor, updated_by=actor, **data)
            keep.append(row.pk)
        partner.bank_accounts.exclude(pk__in=keep).delete()

    @staticmethod
    def _replace_contacts(partner, contacts):
        if contacts is None:
            return
        partner.contacts.all().delete()
        PartnerContact.objects.bulk_create(
            [PartnerContact(partner=partner, **contact) for contact in contacts if contact.get("name")]
        )


PartnerBankAccountSerializer = serializer_for(PartnerBankAccount)


PartnerCompanySerializer = serializer_for(PartnerCompany)


PartnerContactSerializer = serializer_for(PartnerContact)


ProductCategorySerializer = serializer_for(ProductCategory)


TaxCodeSerializer = serializer_for(TaxCode)


UomSerializer = serializer_for(Uom)


UomCategorySerializer = serializer_for(UomCategory)


WarehouseSerializer = serializer_for(Warehouse)
