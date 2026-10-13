"""Transactional receipt/return sheets; legacy line endpoints use the same rules."""
from io import BytesIO
from pathlib import Path

from django.db import transaction
from django.db.models import Q, Sum
from django.http import FileResponse
from openpyxl import Workbook
from rest_framework import decorators, response, permissions
from django.core.exceptions import ValidationError

from backend import receiving as service
from backend.models import GoodsReceipt, GoodsReceiptLine, PurchaseReturn, PurchaseReturnLine, PurchaseOrderLine, Partner, Location, DocumentEvidence
from .api_common import ApprovalViewSet
from .purchase_workspace_views import errors
from .serializers.common import serializer_for
from .exports import safe_text


def sheet(doc):
    ret=service.returning(doc)
    data=serializer_for(type(doc))(doc).data
    data.update(supplier_code=doc.supplier.code,supplier_name=doc.supplier.name)
    data['lines']=[]
    for line in doc.lines.select_related('purchase_order_line__order','material__uom','uom','source_location' if ret else 'location'):
        po=line.purchase_order_line
        loc=line.source_location if ret else line.location
        row=dict(serializer_for(type(line))(line).data)
        row.update(location_code=loc.code,location_name=loc.name,purchase_order=po.order_id,purchase_number=po.order.number,purchase_line=po.line_number,material_code=line.material.code,
            material_name=line.material.name,specification=line.material.specification,uom_name=line.uom.name,
            inventory_uom=line.material.uom.name,ordered_quantity=str(po.quantity),ordered_spare_quantity=str(po.spare_quantity),
            source_order=po.snapshot.get('source_order',''),source_order_line=po.snapshot.get('source_order_line',''))
        data['lines'].append(row)
    data['attachments']=[dict(id=e.pk,name=Path(e.file.name).name,uploaded_by=e.uploaded_by,uploaded_at=e.uploaded_at)
        for e in DocumentEvidence.objects.filter(document_type=doc._meta.model_name,document_id=doc.pk)]
    return data


class ReceiptSheetViewSet(ApprovalViewSet):
    permission_classes=(permissions.IsAuthenticated,)
    queryset=GoodsReceipt.objects.all()
    serializer_class=serializer_for(GoodsReceipt)
    is_return=False

    @errors
    def list(self,request,*args,**kwargs):
        qs=self.get_queryset().select_related('supplier')
        q=request.query_params.get('q','')
        if q: qs=qs.filter(Q(number__icontains=q)|Q(supplier__name__icontains=q)|Q(supplier__code__icontains=q))
        if request.query_params.get('status'): qs=qs.filter(status=request.query_params['status'])
        if request.query_params.get('unconfirmed')=='1': qs=qs.filter(status='approved',is_confirmed=False)
        page=max(1,int(request.query_params.get('page',1)));count=qs.count()
        if request.query_params.get('workspace')!='1':
            return response.Response(dict(count=count,results=self.get_serializer(qs[(page-1)*50:page*50],many=True).data))
        return response.Response(dict(count=count,results=[dict(id=d.pk,number=d.number,supplier_name=d.supplier.name,
            date=str(d.return_date if self.is_return else d.receipt_date),status=d.status,is_confirmed=d.is_confirmed,
            supplier_delivery_number=getattr(d,'supplier_delivery_number','')) for d in qs[(page-1)*50:page*50]]))

    def retrieve(self,request,*args,**kwargs): return response.Response(sheet(self.get_object()))

    @errors
    @transaction.atomic
    def create(self,request,*args,**kwargs): return response.Response(self.save_sheet(request),status=201)

    @errors
    @transaction.atomic
    def update(self,request,*args,**kwargs):
        doc=self.get_queryset().select_for_update().get(pk=kwargs['pk'])
        return response.Response(self.save_sheet(request,doc))

    def save_sheet(self,request,doc=None):
        data=request.data;actor=request.user.get_username();ret=self.is_return
        if data.get('receipt_type','normal')!='normal': raise ValidationError('非生产收货不在本期范围')
        if data.get('purchase_order'):
            from backend.models import PurchaseOrder
            if PurchaseOrder.objects.get(pk=data['purchase_order']).purchase_type!='production':
                raise ValidationError('外协和非生产收退货不在本期范围')
        allowed={'supplier','site','default_print_person','reason','replenishment','return_location'} if ret else {
            'supplier','site','default_print_person','notes','supplier_delivery_number','iqc_location','raw_location'}
        date_key='return_date' if ret else 'receipt_date';allowed.add(date_key)
        # Full sheets may echo read-only values; they are never assigned from the request.
        if doc:
            service.editable(doc)
            if data.get('version')!=doc.version: raise ValidationError('单据已被修改，请刷新后重试')
        else: doc=self.queryset.model(created_by=actor,default_print_person=request.user.get_full_name() or actor)
        for field in allowed:
            if field in data:
                if field in ('supplier','return_location','iqc_location','raw_location'): setattr(doc,field+'_id',data[field] or None)
                else: setattr(doc,field,data[field])
        if not doc.supplier_id: raise ValidationError('请选择供应商')
        doc.updated_by=actor
        doc.full_clean();doc.save()
        if 'lines' in data:
            old={l.pk:l for l in doc.lines.all()};seen=set();numbers=set();lines=[]
            model=PurchaseReturnLine if ret else GoodsReceiptLine
            parent='purchase_return' if ret else 'receipt'
            # Lock source rows before replacing any reservations.
            ids=[int(r['purchase_order_line']) for r in data['lines']]
            sources={p.pk:p for p in PurchaseOrderLine.objects.select_for_update().select_related('order','material','uom').filter(pk__in=ids).order_by('pk')}
            for index,row in enumerate(data['lines'],1):
                identity=row.get('id');line=old.get(identity) if identity else model(**{parent:doc})
                if line is None or identity in seen: raise ValidationError('明细身份不存在或重复')
                if identity: seen.add(identity)
                number=int(row.get('line_number') or index*10)
                if number<=0 or number in numbers: raise ValidationError('行号必须为不重复的正整数')
                numbers.add(number)
                po=sources[int(row['purchase_order_line'])]
                if identity and (line.line_number!=number or line.purchase_order_line_id!=po.pk): raise ValidationError('已保存行不能改行号或采购来源，请删行后重新生成')
                line.line_number=number;line.purchase_order_line=po;line.material=po.material;line.uom=po.uom
                if not identity:
                    line.uom_rate_m=po.uom_rate_m;line.uom_rate_d=po.uom_rate_d
                line.quantity=service.decimal(row.get('quantity'));line.spare_quantity=service.decimal(row.get('spare_quantity'))
                line.batch_number=row.get('batch_number','')
                if ret:
                    line.source_location_id=row.get('source_location') or doc.return_location_id
                    line.reason=row.get('reason','')
                else:
                    line.location_id=row.get('location');line.notes=row.get('notes','')
                    line.pending_quantity=0
                line.full_clean(exclude=['accepted_quantity','rejected_quantity'] if not ret else [])
                lines.append(line)
            service.validate_document(doc,lines)
            doc.lines.exclude(pk__in=seen).delete()
            for line in lines: line.save()
            orders={l.purchase_order_line.order_id for l in lines};doc.purchase_order_id=next(iter(orders)) if len(orders)==1 else None
        elif doc.lines.exists():
            service.validate_document(doc,list(doc.lines.all()))
        doc.version+=1;doc.save();service.audit(doc,'save',actor)
        return sheet(doc)

    @errors
    @transaction.atomic
    def destroy(self,request,*args,**kwargs):
        doc=self.get_queryset().select_for_update().get(pk=kwargs['pk']);service.editable(doc)
        service.audit(doc,'delete',request.user.get_username());doc.delete()
        return response.Response(status=204)

    @errors
    @transaction.atomic
    def transition(self,obj,action,actor='',reason=''):
        doc=self.get_queryset().select_for_update().get(pk=obj.pk)
        actor=actor or self.request.user.get_username()
        if self.request.data.get('version') is not None and self.request.data['version']!=doc.version:
            raise ValidationError('单据已被修改，请刷新')
        if action=='approve': service.approve_document(doc,actor)
        elif action=='unapprove': service.unapprove_document(doc,actor)
        elif action in ('confirm','unconfirm'):
            if self.is_return: raise ValidationError('采购退货不使用回单确认')
            if action=='confirm':
                attachments=DocumentEvidence.objects.filter(document_type='goodsreceipt',document_id=doc.pk,evidence_type='supplier_delivery')
                if not any(a.file and a.file.storage.exists(a.file.name) for a in attachments): raise ValidationError('请先上传本单有效回单附件')
                doc.confirm(actor)
            else: doc.unconfirm()
            doc.version+=1;doc.save();service.audit(doc,action,actor)
        elif action=='submit': doc.submit();doc.save()
        else: raise ValidationError('请使用保存、审核、反审核及回单操作')
        return response.Response(sheet(doc))

    @decorators.action(detail=False,methods=['get'])
    @errors
    def lookups(self,request):
        kind=request.query_params.get('kind');q=request.query_params.get('q','');site=request.query_params.get('site','1000')
        if kind=='supplier':
            qs=Partner.objects.filter(kind__in=('supplier','both')).filter(Q(code__icontains=q)|Q(name__icontains=q)|Q(short_name__icontains=q))
            return response.Response([dict(id=p.pk,code=p.code,name=p.name,short_name=p.short_name) for p in qs.order_by('code')[:100]])
        qs=Location.objects.filter(Q(source_site=site)|Q(source_site='')).filter(Q(code__icontains=q)|Q(name__icontains=q))
        return response.Response([dict(id=p.pk,code=p.code,name=p.name,disabled=p.disabled_for_inventory) for p in qs.order_by('code')])

    @decorators.action(detail=False,methods=['get'])
    @errors
    def candidates(self,request):
        params=request.query_params
        qs=PurchaseOrderLine.objects.filter(order__supplier_id=params['supplier'],order__site=params.get('site','1000'),
            order__purchase_type='production',order__status='approved').select_related('order','material__default_location','material__uom','uom')
        if not self.is_return: qs=qs.exclude(line_status__in=('C','c','closed'))
        if params.get('q'): qs=qs.filter(Q(order__number__icontains=params['q'])|Q(material__code__icontains=params['q'])|Q(material__name__icontains=params['q']))
        for param,field in [('order_from','order__number__gte'),('order_to','order__number__lte'),('date_from','order__order_date__gte'),('date_to','order__order_date__lte')]:
            if params.get(param):qs=qs.filter(**{field:params[param]})
        rows=[]
        line_model,parent=(PurchaseReturnLine,'purchase_return') if self.is_return else (GoodsReceiptLine,'receipt')
        reservations=line_model.objects.filter(purchase_order_line__in=qs,**{parent+'__posted':False}).exclude(**{parent+'__status':'void'})
        if params.get('document'): reservations=reservations.exclude(**{parent+'_id':params['document']})
        reserved_by_po={r['purchase_order_line_id']:(r['q'] or 0,r['s'] or 0) for r in reservations.order_by().values('purchase_order_line_id').annotate(q=Sum('quantity'),s=Sum('spare_quantity'))}
        for po in qs.order_by('order__number','line_number').iterator(chunk_size=500):
            reserved,spare_reserved=reserved_by_po.get(po.pk,(0,0))
            q=(po.received_quantity-po.returned_quantity if self.is_return else po.quantity+po.over_receipt_quantity-po.received_quantity)-reserved
            s=(po.received_spare_quantity-po.returned_spare_quantity if self.is_return else po.spare_quantity-po.received_spare_quantity)-spare_reserved
            if q<=0 and s<=0:continue
            rows.append(dict(purchase_order_line=po.pk,purchase_number=po.order.number,purchase_line=po.line_number,
                material_code=po.material.code,material_name=po.material.name,specification=po.material.specification,
                ordered_quantity=str(po.quantity),ordered_spare_quantity=str(po.spare_quantity),received_quantity=str(po.received_quantity),
                received_spare_quantity=str(po.received_spare_quantity),reserved_quantity=str(reserved),reserved_spare_quantity=str(spare_reserved),
                available_quantity=str(q),available_spare_quantity=str(s),quantity=str(max(q,0)),spare_quantity=str(max(s,0)),
                uom_name=po.uom.name,inventory_uom=po.material.uom.name,uom_rate_m=str(po.uom_rate_m),uom_rate_d=str(po.uom_rate_d),
                location=po.material.default_location_id,source_location=po.material.default_location_id,batch_number='',notes='',reason=''))
            if len(rows) == 500: break
        return response.Response(rows)

    @decorators.action(detail=True,methods=['get'])
    def shortage(self,request,pk=None):
        self.get_object()
        return response.Response(dict(applicable=False,message='本单为普通采购，不适用外协收货缺料检查。'))

    @decorators.action(detail=True,methods=['post'])
    @transaction.atomic
    def print(self,request,pk=None):
        doc=self.get_queryset().select_for_update().get(pk=pk);doc.print_count+=1;doc.save(update_fields=['print_count'])
        service.audit(doc,'print',request.user.get_username());return response.Response(sheet(doc))

    @decorators.action(detail=True,methods=['post'])
    def export(self,request,pk=None):
        doc=self.get_object();data=sheet(doc);wb=Workbook();ws=wb.active;ws.title='采购退货' if self.is_return else '采购收货'
        ws.append(['单号',safe_text(doc.number),'供应商',safe_text(doc.supplier.name)])
        columns=[('line_number','行号'),('purchase_number','采购单号'),('purchase_line','采购行号'),('material_code','物料编码'),('material_name','物料名称'),('quantity','正式数量'),('spare_quantity','备品数量'),('uom_name','采购单位'),('batch_number','批号')]
        ws.append([label for _,label in columns])
        for row in data['lines']:ws.append([safe_text(str(row.get(key,''))) for key,_ in columns])
        stream=BytesIO();wb.save(stream);stream.seek(0)
        return FileResponse(stream,as_attachment=True,filename=doc.number+'.xlsx')


class GoodsReceiptViewSet(ReceiptSheetViewSet): pass


class PurchaseReturnViewSet(ReceiptSheetViewSet):
    queryset=PurchaseReturn.objects.all()
    serializer_class=serializer_for(PurchaseReturn)
    is_return=True


class ReceiptLineViewSet(ApprovalViewSet):
    permission_classes=(permissions.IsAuthenticated,)
    queryset=GoodsReceiptLine.objects.all()
    serializer_class=serializer_for(GoodsReceiptLine)

    def get_queryset(self):
        qs=super().get_queryset()
        parent='purchase_return' if self.queryset.model is PurchaseReturnLine else 'receipt'
        if self.request.query_params.get(parent): qs=qs.filter(**{parent+'_id':self.request.query_params[parent]})
        return qs

    @errors
    @transaction.atomic
    def perform_create(self,serializer):
        values=serializer.validated_data
        parent=values.get('receipt') or values.get('purchase_return');parent=type(parent).objects.select_for_update().get(pk=parent.pk)
        service.editable(parent)
        po=PurchaseOrderLine.objects.select_for_update().get(pk=values['purchase_order_line'].pk)
        protected={'accepted_quantity','rejected_quantity','pending_quantity','replacement_line','iqc_number','iqc_line','source_object','uom_rate_m','uom_rate_d'}
        if protected.intersection(self.request.data): raise ValidationError('系统关联字段不能手工赋值')
        obj=serializer.save(material=po.material,uom=po.uom,uom_rate_m=po.uom_rate_m,uom_rate_d=po.uom_rate_d)
        service.validate_document(parent,list(parent.lines.all()))
        orders=set(parent.lines.values_list('purchase_order_line__order_id',flat=True))
        parent.purchase_order_id=next(iter(orders)) if len(orders)==1 else None
        parent.version+=1;parent.save()

    @errors
    def update(self,request,*args,**kwargs):
        raise ValidationError('请在收退货工作台保存完整单据')

    @errors
    def destroy(self,request,*args,**kwargs):
        raise ValidationError('请在收退货工作台删除明细后保存')


class GoodsReceiptLineViewSet(ReceiptLineViewSet): pass


class PurchaseReturnLineViewSet(ReceiptLineViewSet):
    queryset=PurchaseReturnLine.objects.all()
    serializer_class=serializer_for(PurchaseReturnLine)
