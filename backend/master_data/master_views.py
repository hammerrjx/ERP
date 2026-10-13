from rest_framework import decorators, response
from backend.domain.master_data import (
    AccountingAccount,
    BusinessGroup,
    Company,
    Currency,
    CurrencyRate,
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
from backend.models import CustomerAddress, DocumentEvidence
from .api_common import ensure_editable, ensure_status_unchanged, make_viewset
from .serializers.common import serializer_for
from .serializers.master_data import (
    BusinessGroupSerializer,
    CompanySerializer,
    CurrencyRateSerializer,
    CurrencySerializer,
    CustomerAddressSerializer,
    LocationSerializer,
    MaterialCompanySerializer,
    MaterialSerializer,
    MaterialUomConversionSerializer,
    PartnerBankAccountSerializer,
    PartnerCompanySerializer,
    PartnerContactSerializer,
    PartnerSerializer,
    PaymentMethodSerializer,
    ProductCategorySerializer,
    TaxCodeSerializer,
    UomCategorySerializer,
    UomSerializer,
    WarehouseSerializer,
)
from .serializers.system import (
    DocumentEvidenceSerializer,
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
    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticated
        receipt=self.request.data.get('document_type')=='goodsreceipt' or self.request.query_params.get('document_type')=='goodsreceipt'
        if self.kwargs.get('pk'):
            receipt=DocumentEvidence.objects.filter(pk=self.kwargs['pk'],document_type='goodsreceipt').exists()
        return [IsAuthenticated()] if receipt else super().get_permissions()

    def perform_create(self, serializer):
        from django.db import transaction
        from rest_framework.exceptions import ValidationError
        from backend.models import GoodsReceipt
        from pathlib import Path
        data=serializer.validated_data
        if data.get('document_type') == 'goodsreceipt':
            with transaction.atomic():
                doc=GoodsReceipt.objects.select_for_update().filter(pk=data['document_id']).first()
                if not doc: raise ValidationError('收货单不存在')
                if doc.is_confirmed: raise ValidationError('已确认回单的凭证不可变更，请先反回单确认')
                if data.get('evidence_type') != 'supplier_delivery': raise ValidationError('收货单必须上传供应商送货回单')
                file=data.get('file')
                if not file or file.size <= 0 or file.size > 20*1024*1024 or Path(file.name).suffix.lower() not in ('.pdf','.png','.jpg','.jpeg'):
                    raise ValidationError('请上传20MB以内的PDF、PNG或JPEG回单')
                signature=file.read(8);file.seek(0)
                suffix=Path(file.name).suffix.lower()
                valid=(suffix=='.pdf' and signature.startswith(b'%PDF-')) or (suffix=='.png' and signature==b'\x89PNG\r\n\x1a\n') or (suffix in ('.jpg','.jpeg') and signature.startswith(b'\xff\xd8\xff'))
                if not valid: raise ValidationError('文件内容与PDF/图片格式不符')
                serializer.save(uploaded_by=self.request.user.get_username(),document_number=doc.number)
        else: serializer.save(uploaded_by=self.request.user.get_username())

    def update(self, request, *args, **kwargs):
        from rest_framework.exceptions import ValidationError
        if self.get_object().document_type == 'goodsreceipt' or request.data.get('document_type')=='goodsreceipt': raise ValidationError('回单附件不可覆盖，请删除后重新上传')
        return super().update(request,*args,**kwargs)

    def destroy(self, request, *args, **kwargs):
        from django.db import transaction
        from rest_framework.exceptions import ValidationError
        from backend.models import GoodsReceipt
        with transaction.atomic():
            obj=self.get_object()
            if obj.document_type=='goodsreceipt':
                doc=GoodsReceipt.objects.select_for_update().filter(pk=obj.document_id).first()
                if doc and doc.is_confirmed: raise ValidationError('已确认回单的附件不能删除')
            return super().destroy(request,*args,**kwargs)

    from rest_framework.decorators import action
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        from django.http import FileResponse, Http404
        obj=self.get_object()
        if not obj.file or not obj.file.storage.exists(obj.file.name): raise Http404('附件不存在')
        return FileResponse(obj.file.open('rb'),as_attachment=True)


class CurrencyViewSet(make_viewset(Currency, CurrencySerializer)):
    queryset = Currency.objects.order_by('code')

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        if Currency.objects.filter(source_object='dgyzx1.ex_mstr').exists():
            raise ValidationError('本账套货币与dgyzx1统一，请在源库新增后同步')
        super().perform_create(serializer)

    def perform_update(self, serializer):
        from rest_framework.exceptions import ValidationError
        if Currency.objects.filter(pk=serializer.instance.pk, source_object='dgyzx1.ex_mstr').exists():
            raise ValidationError('源库货币由dgyzx1同步维护，请修改源资料后重新同步')
        super().perform_update(serializer)

    def destroy(self, request, *args, **kwargs):
        from rest_framework.exceptions import ValidationError
        if self.get_object().source_object == 'dgyzx1.ex_mstr':
            raise ValidationError('源库货币不能在本地删除')
        return super().destroy(request, *args, **kwargs)

    def transition(self, obj, action, actor='', reason=''):
        from rest_framework.exceptions import ValidationError
        if obj.source_object == 'dgyzx1.ex_mstr':
            raise ValidationError('源库货币不使用本地审核或作废流程')
        return super().transition(obj, action, actor, reason)
AccountingAccountViewSet = make_viewset(AccountingAccount, serializer_for(AccountingAccount))
class CurrencyRateViewSet(make_viewset(CurrencyRate, CurrencyRateSerializer)):
    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        if serializer.validated_data['currency'].source_object == 'dgyzx1.ex_mstr':
            raise ValidationError('本账套汇率与dgyzx1统一，请在源库维护后同步')
        super().perform_create(serializer)
    def perform_update(self, serializer):
        from rest_framework.exceptions import ValidationError
        if CurrencyRate.objects.filter(pk=serializer.instance.pk, source_object='dgyzx1.exd_det').exists():
            raise ValidationError('源库汇率由dgyzx1同步维护')
        super().perform_update(serializer)

    def destroy(self, request, *args, **kwargs):
        from rest_framework.exceptions import ValidationError
        if self.get_object().source_object == 'dgyzx1.exd_det':
            raise ValidationError('源库汇率不能在本地删除')
        return super().destroy(request, *args, **kwargs)
LocationViewSet = make_viewset(Location, LocationSerializer)
class MaterialViewSet(make_viewset(Material, MaterialSerializer)):
    queryset = Material.objects.select_related('category', 'uom', 'default_location', 'tax_master').prefetch_related('used_in_companies')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params.get('lookup') == 'warehouse':
            from django.db.models import Q
            fields = ('id', 'code', 'name', 'specification', 'english_name', 'uom', 'active', 'no_stock_movement', 'batch_control')
            q = request.query_params.get('q', '').strip()
            candidates = queryset.filter(active=True, no_stock_movement=False)
            if q:
                candidates = candidates.filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(specification__icontains=q))
            rows = list(candidates.order_by('code', 'pk').values(*fields)[:50])
            ids = [int(pk) for pk in request.query_params.get('ids', '').split(',') if pk.isdigit()]
            if ids:
                rows.extend(queryset.filter(pk__in=ids).exclude(pk__in=[r['id'] for r in rows]).values(*fields))
            return response.Response(rows)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        # Keep the existing full-list API while bounding each relation prefetch.
        # A single IN query for all imported materials exceeds SQLite's variable limit.
        return response.Response(self.get_serializer(queryset.iterator(chunk_size=500), many=True).data)

    @decorators.action(detail=False, methods=['get'], url_path='sales-candidates')
    def sales_candidates(self, request):
        from django.db.models import Q
        q = request.query_params.get('q', '').strip()
        qs = self.get_queryset()
        if q:
            qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q) | Q(specification__icontains=q))
        if request.query_params.get('usage') == 'purchase':
            qs = qs.filter(status='approved', active=True)
        return response.Response(self.get_serializer(qs.order_by('code')[:50], many=True).data)

    def searched(self, params):
        from django.db.models import Q
        qs = self.get_queryset()
        code, q, category = (str(params.get(k, '')).strip() for k in ('code', 'q', 'category'))
        if code:
            qs = qs.filter(**{'code__iexact' if params.get('exact') == '1' else 'code__istartswith': code})
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(specification__icontains=q))
        if category:
            qs = qs.filter(Q(category__code__icontains=category) | Q(category__name__icontains=category))
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        if params.get('active') in ('0', '1'):
            qs = qs.filter(active=params['active'] == '1')
        return qs.order_by('code', 'pk')

    @decorators.action(detail=False, methods=['get'])
    def search(self, request):
        from .inventory_snapshot_views import integer
        page = integer(request.query_params, 'page', 1)
        size = integer(request.query_params, 'page_size', 50, 100)
        qs = self.searched(request.query_params)
        count = qs.count()
        page = min(page, max(1, (count + size - 1) // size))
        fields = ['id', 'code', 'name', 'specification', 'category__code', 'uom__code',
                  'default_location__code', 'supply_method', 'status', 'active']
        rows = [{k.replace('__', '_'): v for k, v in row.items()}
                for row in qs.values(*fields)[(page-1)*size:page*size]]
        return response.Response(dict(results=rows, count=count, page=page, page_size=size))

    @decorators.action(detail=False, methods=['get'])
    def candidates(self, request):
        from django.db.models import Q
        from rest_framework.exceptions import ValidationError
        models = {'categories': ProductCategory, 'uoms': Uom, 'taxCodes': TaxCode, 'locations': Location, 'suppliers': Partner}
        kind = request.query_params.get('kind')
        if kind not in models:
            raise ValidationError('未知候选类型')
        model = models[kind]
        qs = model.objects.all()
        if kind == 'suppliers':
            qs = qs.filter(kind__in=['supplier', 'both'])
        q = request.query_params.get('q', '').strip()
        matching = qs.filter(Q(code__icontains=q) | Q(name__icontains=q)).order_by('code')
        ids = list(matching.values_list('pk', flat=True)[:50])
        selected = request.query_params.get('selected', '')
        if selected.isdigit():
            ids.append(int(selected))
        fields = ['id', 'code', 'name', 'status']
        if kind == 'categories':
            fields += ['default_uom', 'default_location', 'supply_method', 'part_type', 'product_group', 'buyer', 'quality_control', 'phantom', 'roll', 'batch_control', 'batch_rule']
        if kind == 'taxCodes':
            fields += ['active', 'invoice_name']
        if kind == 'suppliers':
            fields += ['kind', 'currency', 'tax_rate', 'quote_tax_included']
        rows = list(qs.filter(pk__in=ids).order_by('code').values(*fields))
        return response.Response(rows)

    @decorators.action(detail=False, methods=['post'], url_path='search-export')
    def search_export(self, request):
        from .exports import definition_for, workbook_response
        from rest_framework.exceptions import ValidationError
        filters = request.data.get('filters', {})
        if not isinstance(filters, dict):
            raise ValidationError('查询条件格式错误')
        definition = definition_for(Material)
        qs = self.searched(filters)
        if definition.select_related:
            qs = qs.select_related(*definition.select_related)
        if definition.prefetch_related:
            qs = qs.prefetch_related(*definition.prefetch_related)
        return workbook_response(definition, qs)

MaterialCompanyViewSet = make_viewset(MaterialCompany, MaterialCompanySerializer)
MaterialUomConversionViewSet = make_viewset(MaterialUomConversion, MaterialUomConversionSerializer)
PartnerViewSet = make_viewset(Partner, PartnerSerializer)
PartnerViewSet.queryset = Partner.objects.select_related('currency', 'payment_method_master').prefetch_related('contacts', 'bank_accounts')
PaymentMethodViewSet = make_viewset(PaymentMethod, PaymentMethodSerializer)
PartnerBankAccountViewSet = make_viewset(PartnerBankAccount, PartnerBankAccountSerializer)
PartnerCompanyViewSet = make_viewset(PartnerCompany, PartnerCompanySerializer)
PartnerContactViewSet = make_viewset(PartnerContact, PartnerContactSerializer)
ProductCategoryViewSet = make_viewset(ProductCategory, ProductCategorySerializer)
TaxCodeViewSet = make_viewset(TaxCode, TaxCodeSerializer)
TaxCodeViewSet.queryset = TaxCode.objects.filter(active=True)
UomViewSet = make_viewset(Uom, UomSerializer)
UomCategoryViewSet = make_viewset(UomCategory, UomCategorySerializer)
WarehouseViewSet = make_viewset(Warehouse, WarehouseSerializer)
