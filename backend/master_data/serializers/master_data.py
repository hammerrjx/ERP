from django.db import transaction
from rest_framework import serializers

from backend.models import (
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


CurrencyRateSerializer = serializer_for(CurrencyRate)


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


MaterialSerializer = serializer_for(Material)


MaterialCompanySerializer = serializer_for(MaterialCompany)


MaterialUomConversionSerializer = serializer_for(MaterialUomConversion)


class PartnerContactInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerContact
        fields = ("name", "position", "phone", "fax", "email", "is_primary")


class PartnerSerializer(BaseSerializer):
    contacts = PartnerContactInputSerializer(many=True, required=False)
    payment_method_name = serializers.CharField(source="payment_method_master.description", read_only=True)

    class Meta:
        model = Partner
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "updated_by", "updated_at")

    def validate(self, attrs):
        contacts = attrs.pop("contacts", None)
        master = attrs.get("payment_method_master")
        if master:
            attrs["payment_method"] = master.code
        elif attrs.get("payment_method"):
            attrs["payment_method_master"] = PaymentMethod.objects.filter(code=attrs["payment_method"]).first()
        attrs = super().validate(attrs)
        if contacts is not None and len(contacts) > 4:
            raise serializers.ValidationError({"contacts": "最多可保存 4 个联系方式"})
        attrs["contacts"] = contacts
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        contacts = validated_data.pop("contacts", None)
        partner = Partner.objects.create(**validated_data)
        self._replace_contacts(partner, contacts)
        return partner

    @transaction.atomic
    def update(self, instance, validated_data):
        contacts = validated_data.pop("contacts", None)
        for name, value in validated_data.items():
            setattr(instance, name, value)
        instance.save()
        self._replace_contacts(instance, contacts)
        return instance

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
