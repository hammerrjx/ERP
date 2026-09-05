from backend.domain.master_data import (
    BusinessGroup, Company, Currency, CurrencyRate, Location, Material, MaterialCompany,
    MaterialUomConversion, Partner, PartnerBankAccount, PartnerCompany, PartnerContact, PaymentMethod,
    ProductCategory, TaxCode, Uom, UomCategory, Warehouse,
)
from backend.models import CustomerAddress, DocumentEvidence
from .api_common import ensure_editable, ensure_status_unchanged, make_viewset
from .serializers import (
    BusinessGroupSerializer, CompanySerializer, CurrencyRateSerializer, CurrencySerializer, CustomerAddressSerializer, DocumentEvidenceSerializer, LocationSerializer,
    MaterialCompanySerializer, MaterialSerializer, MaterialUomConversionSerializer,
    PartnerBankAccountSerializer, PartnerCompanySerializer, PartnerContactSerializer,
    PartnerSerializer, PaymentMethodSerializer, ProductCategorySerializer, TaxCodeSerializer, UomCategorySerializer,
    UomSerializer, WarehouseSerializer,
)

CompanyViewSet = make_viewset(Company, CompanySerializer)
BusinessGroupViewSet = make_viewset(BusinessGroup, BusinessGroupSerializer)


class CustomerAddressViewSet(make_viewset(CustomerAddress, CustomerAddressSerializer)):
    def perform_create(self, serializer):
        actor = self.request.user.get_username() or "system"
        serializer.save(created_by=actor, source_key="")

    def perform_update(self, serializer):
        ensure_editable(serializer.instance)
        ensure_status_unchanged(serializer)
        serializer.save(updated_by=self.request.user.get_username() or "system")


class DocumentEvidenceViewSet(make_viewset(DocumentEvidence, DocumentEvidenceSerializer)):
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user.get_username())
CurrencyViewSet = make_viewset(Currency, CurrencySerializer)
CurrencyRateViewSet = make_viewset(CurrencyRate, CurrencyRateSerializer)
LocationViewSet = make_viewset(Location, LocationSerializer)
MaterialViewSet = make_viewset(Material, MaterialSerializer)
MaterialCompanyViewSet = make_viewset(MaterialCompany, MaterialCompanySerializer)
MaterialUomConversionViewSet = make_viewset(MaterialUomConversion, MaterialUomConversionSerializer)
PartnerViewSet = make_viewset(Partner, PartnerSerializer)
PaymentMethodViewSet = make_viewset(PaymentMethod, PaymentMethodSerializer)
PartnerBankAccountViewSet = make_viewset(PartnerBankAccount, PartnerBankAccountSerializer)
PartnerCompanyViewSet = make_viewset(PartnerCompany, PartnerCompanySerializer)
PartnerContactViewSet = make_viewset(PartnerContact, PartnerContactSerializer)
ProductCategoryViewSet = make_viewset(ProductCategory, ProductCategorySerializer)
TaxCodeViewSet = make_viewset(TaxCode, TaxCodeSerializer)
UomViewSet = make_viewset(Uom, UomSerializer)
UomCategoryViewSet = make_viewset(UomCategory, UomCategorySerializer)
WarehouseViewSet = make_viewset(Warehouse, WarehouseSerializer)
