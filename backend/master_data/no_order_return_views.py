from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError as ModelError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import decorators, response, serializers, viewsets

from backend.models import (SalesReturn, SalesReturnLine, Material, CustomerMaterial, CurrencyRate,
    Employee, InventoryDictionary, AuditEvent, InventoryPostingControl)
from backend.no_order_returns import derive_line, amount, post_return, unpost_return
from .api_common import ErpRolePermission
from .serializers.delivery import SalesReturnSerializer, SalesReturnLineSerializer


def default_printer():
    return InventoryDictionary.objects.filter(dictionary='RETURN_DEFAULT', code='printer', disabled=False).values_list('name', flat=True).first() or ''


def payload(doc):
    data = SalesReturnSerializer(doc).data
    data['customer_code'], data['customer_name'] = doc.customer.code, doc.customer.name
    data['lines'] = []
    total = Decimal(0)
    people = dict(Employee.objects.values_list('code', 'name'))
    for line in doc.lines.select_related('material', 'uom', 'inventory_uom', 'return_location'):
        row = dict(SalesReturnLineSerializer(line).data)
        row.update(uom_name=line.uom.name, inventory_uom_name=line.inventory_uom.name if line.inventory_uom_id else '',
            location_code=line.return_location.code, location_name=line.return_location.name, amount=str(amount(line)),
            created_name=people.get(line.created_by, ''), updated_name=people.get(line.updated_by, ''))
        total += amount(line)
        data['lines'].append(row)
    data['amount'] = str(total)
    data['posting_enabled'] = getattr(settings, 'ERP_NO_ORDER_RETURN_POST_STOCK', False)
    return data


class ReturnLineInput(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = SalesReturnLine
        fields = ('id', 'material', 'customer_material', 'quantity', 'spare_quantity', 'unit_price', 'return_location', 'batch_number', 'notes')


class NoOrderReturnPermission(ErpRolePermission):
    def has_permission(self, request, view):
        view.basename = 'sales-return'
        return super().has_permission(request, view)


class NoOrderReturnViewSet(viewsets.ViewSet):
    permission_classes = (NoOrderReturnPermission,)

    @decorators.action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        from .exports import ExportDefinition, c, workbook_response
        doc = self.get_doc(pk)
        definition = ExportDefinition('SLCRMTA2', '无订单退货', (
            c('退货单号', 'sales_return.number'), c('日期', 'sales_return.return_date', 'date'),
            c('客户', 'sales_return.customer.code'), c('客户PO', 'sales_return.customer_po'),
            c('行号', 'line_number', 'number'), c('物料编码', 'material.code'), c('客户物料编码', 'customer_material_code'),
            c('物料名称', 'material_name'), c('物料规格', 'material_specification'),
            c('退货数量', 'quantity', 'number'), c('退备品数', 'spare_quantity', 'number'), c('销售单位', 'uom.name'),
            c('单价', 'unit_price', 'number'), c('金额', amount, 'number'), c('退入库位', 'return_location.code'),
            c('库位名称', 'return_location.name'), c('批号', 'batch_number'), c('备注', 'notes'),
            c('单位换算率(分子)', 'uom_rate_m', 'number'), c('单位换算率(分母)', 'uom_rate_d', 'number'),
            c('库存单位', 'inventory_uom.name'), c('录入人', 'created_by'), c('录入时间', 'created_at', 'datetime'),
            c('修改次数', 'modification_count', 'number'), c('修改人', 'updated_by'), c('修改时间', 'updated_at', 'datetime'),
            c('客户终端物料编码', 'terminal_customer_code'), c('客户终端物料名称', 'terminal_customer_name'),
        ))
        return workbook_response(definition, doc.lines.select_related('sales_return__customer', 'material', 'uom', 'inventory_uom', 'return_location'))

    @decorators.action(detail=False, methods=['get'])
    def defaults(self, request):
        return response.Response({
            'posting_enabled': getattr(settings, 'ERP_NO_ORDER_RETURN_POST_STOCK', False),
            'default_print_person': default_printer(),
            'groups': list(Employee.objects.filter(group_code='SDGROUP', is_locked=False).values('code', 'name')),
            'addresses': list(InventoryDictionary.objects.filter(dictionary='DN_ADDR', disabled=False).values('code', 'name')),
            'sites': list(InventoryPostingControl.objects.values_list('site', flat=True)),
            'rates': list(CurrencyRate.objects.values('currency_id', 'effective_date', 'expiry_date', 'rate_to_company')),
        })

    def get_doc(self, pk, lock=False):
        qs = SalesReturn.objects.filter(no_order=True).select_related('customer', 'currency')
        if lock:
            qs = qs.select_for_update()
        from django.shortcuts import get_object_or_404
        return get_object_or_404(qs, pk=pk)

    def list(self, request):
        qs = SalesReturn.objects.filter(no_order=True).select_related('customer')
        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(Q(number__icontains=search) | Q(customer__code__icontains=search) | Q(customer__name__icontains=search) | Q(customer_po__icontains=search))
        page = serializers.IntegerField(min_value=1).run_validation(request.query_params.get('page', 1))
        return response.Response({'count': qs.count(), 'page': page, 'page_size': 50, 'results': [
            {**SalesReturnSerializer(d).data, 'customer_name': d.customer.name, 'customer_code': d.customer.code}
            for d in qs[(page-1)*50:page*50]]})

    def retrieve(self, request, pk=None):
        return response.Response(payload(self.get_doc(pk)))

    @transaction.atomic
    def create(self, request):
        return self.save_document(request)

    @transaction.atomic
    def partial_update(self, request, pk=None):
        return self.save_document(request, self.get_doc(pk, True))

    def save_document(self, request, doc=None):
        actor = request.user.get_username()
        creating = doc is None
        previous_rate_identity = (doc.currency_id, doc.return_date) if doc else None
        previous_customer = doc.customer_id if doc else None
        if doc and (doc.posted or doc.source_key or doc.status not in ('draft', 'rejected')):
            raise serializers.ValidationError('已审核、待审核或历史单据不可修改')
        if doc and request.data.get('revision') != doc.revision:
            raise serializers.ValidationError('单据已被其他操作更新，请重新查询')
        allowed = {'customer', 'return_date', 'currency', 'tax_rate', 'customer_po', 'business_group', 'delivery_address', 'reason', 'site'}
        if set(request.data) - allowed - {'revision', 'lines'}:
            raise serializers.ValidationError('自动关联字段不能手工提交')
        head = {k: v for k, v in request.data.items() if k in allowed}
        serializer = SalesReturnSerializer(doc, data={**head, 'no_order': True}, partial=bool(doc))
        serializer.is_valid(raise_exception=True)
        lines = ReturnLineInput(data=request.data.get('lines', []), many=True)
        lines.is_valid(raise_exception=True)
        if not lines.validated_data:
            raise serializers.ValidationError('至少填写一条明细')
        # A material selection may identify a customer-material association; values remain derived.
        line_allowed = set(ReturnLineInput().fields)
        if any(set(raw) - line_allowed for raw in request.data.get('lines', [])):
            raise serializers.ValidationError('明细中包含不可编辑的关联字段')
        old = {l.pk: l for l in doc.lines.all()} if doc else {}
        seen = set()
        for raw in lines.validated_data:
            key = raw.get('id')
            if key is not None and (key not in old or key in seen):
                raise serializers.ValidationError('明细不属于本单或重复')
            if key:
                seen.add(key)
        try:
            doc = serializer.save(**({'created_by': actor} if not doc else {}), updated_by=actor)
            if not doc.currency_id:
                doc.currency = doc.customer.currency
            if not doc.currency_id:
                raise ModelError('客户未设置默认币种，请选择币种')
            if doc.tax_rate < 0 or doc.tax_rate > 100:
                raise ModelError('增值税率必须在0至100之间')
            if not doc.customer_po.strip():
                raise ModelError('客户PO必填')
            if not Employee.objects.filter(code=doc.business_group, group_code='SDGROUP', is_locked=False).exists():
                raise ModelError('业务组别须为未锁定的 SDGROUP 用户')
            if doc.delivery_address and not InventoryDictionary.objects.filter(dictionary='DN_ADDR', name=doc.delivery_address, disabled=False).exists():
                raise ModelError('送货地址未在通用代码 DN_ADDR 中定义或已禁用')
            from backend.currencies import exchange_rate
            if previous_rate_identity != (doc.currency_id, doc.return_date):
                doc.exchange_rate = exchange_rate(doc.currency, doc.return_date)
            doc.default_print_person = default_printer()
            doc.revision += 1
            doc.full_clean()
            doc.save()
            number = max((l.line_number for l in old.values()), default=0)
            now = timezone.now()
            for raw in lines.validated_data:
                values = dict(raw)
                key = values.pop('id', None)
                line = old.get(key)
                previous_identity = (line.material_id, line.customer_material_id) if line else None
                if line is None:
                    number += 10
                    line = SalesReturnLine(sales_return=doc, line_number=number, created_by=actor, created_at=now)
                for name, value in values.items():
                    setattr(line, name, value)
                line.sales_return = doc
                if line.return_location.source_site != doc.site or line.return_location.disabled_for_inventory:
                    raise ModelError('退入库位必须属于单据站点且未停用')
                # Keep saved snapshots unless the material association/customer has changed.
                if previous_identity != (line.material_id, line.customer_material_id) or previous_customer != doc.customer_id or not line.inventory_uom_id:
                    derive_line(line)
                line.updated_by, line.updated_at = actor, now
                line.modification_count += bool(key)
                line.full_clean()
                line.save()
            removed = set(old) - seen
            if any(old[k].sales_history.exists() for k in removed):
                raise ModelError('已有退货历史的明细不能删除，请保留审计依据')
            doc.lines.filter(pk__in=removed).delete()
        except ModelError as exc:
            raise serializers.ValidationError(getattr(exc, 'message_dict', exc.messages)) from exc
        AuditEvent.objects.create(model=doc._meta.label_lower, object_id=str(doc.pk), action='save_sheet', actor=actor)
        return response.Response(payload(doc), status=201 if creating else 200)

    @transaction.atomic
    def destroy(self, request, pk=None):
        doc = self.get_doc(pk, True)
        if doc.posted or doc.source_key or doc.posting_version:
            raise serializers.ValidationError('已审核、历史或曾经过账的单据不能删除')
        doc.delete()
        return response.Response(status=204)

    def action_document(self, request, pk, action):
        with transaction.atomic():
            doc = self.get_doc(pk, True)
            if request.data.get('revision') != doc.revision:
                raise serializers.ValidationError('单据已更新，请重新查询后操作')
            actor = request.user.get_username()
            link = getattr(request.user, 'employee_link', None)
            stock_actor = link.employee.code if link else actor
            try:
                if action == 'approve':
                    post_return(doc, stock_actor)
                elif action == 'unapprove':
                    unpost_return(doc, stock_actor)
                else:
                    if doc.source_key:
                        raise ModelError('历史单据只读')
                    if action in ('confirm', 'unconfirm'):
                        if action == 'confirm':
                            doc.confirm(actor)
                        else:
                            doc.unconfirm()
                    elif action == 'sign':
                        if doc.status != 'approved':
                            raise ModelError('只有已审核单据可以签收')
                        doc.is_signed, doc.signed_by, doc.signed_at = True, actor, timezone.now()
                    elif action == 'unsign':
                        doc.is_signed, doc.signed_by, doc.signed_at = False, '', None
                    doc.revision += 1
                    doc.save()
            except ModelError as exc:
                raise serializers.ValidationError(exc.messages) from exc
            AuditEvent.objects.create(model=doc._meta.label_lower, object_id=str(doc.pk), action=action, actor=actor)
            return response.Response(payload(doc))

    @decorators.action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        return self.action_document(request, pk, 'approve')

    @decorators.action(detail=True, methods=['post'])
    def unapprove(self, request, pk=None):
        return self.action_document(request, pk, 'unapprove')

    @decorators.action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        return self.action_document(request, pk, 'confirm')

    @decorators.action(detail=True, methods=['post'])
    def unconfirm(self, request, pk=None):
        return self.action_document(request, pk, 'unconfirm')

    @decorators.action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        return self.action_document(request, pk, 'sign')

    @decorators.action(detail=True, methods=['post'])
    def unsign(self, request, pk=None):
        return self.action_document(request, pk, 'unsign')

    @decorators.action(detail=False, methods=['get'])
    def candidates(self, request):
        customer = serializers.IntegerField(min_value=1).run_validation(request.query_params.get('customer'))
        search = request.query_params.get('search', '').strip()
        page = serializers.IntegerField(min_value=1).run_validation(request.query_params.get('page', 1))
        qs = Material.objects.filter(active=True)
        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(name__icontains=search) | Q(customer_materials__customer_id=customer, customer_materials__customer_code__icontains=search)).distinct()
        rows = []
        count = qs.count()
        for material in qs.select_related('uom').order_by('code')[(page-1)*40:page*40]:
            matches = list(CustomerMaterial.objects.filter(customer_id=customer, material=material, enabled=True)) or [None]
            for cp in matches:
                line = SalesReturnLine(material=material, customer_material=cp, sales_return=SalesReturn(customer_id=customer))
                derive_line(line)
                rows.append({'id': f'{material.pk}:{cp.pk if cp else 0}', 'material': material.pk,
                    'customer_material': cp.pk if cp else None, 'material_code': material.code,
                    **{k: str(getattr(line, k)) for k in ('material_name', 'material_specification', 'customer_material_code', 'terminal_customer_code', 'terminal_customer_name', 'uom_rate_m', 'uom_rate_d')},
                    'uom_name': line.uom.name, 'inventory_uom_name': material.uom.name,
                    'return_location': material.default_location_id})
        return response.Response({'results': rows, 'count': count, 'page': page, 'page_size': 40})
