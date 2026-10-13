"""Workspace endpoints retain the established purchase-order and requisition URLs."""
from functools import wraps
from io import BytesIO

from django.core.exceptions import ValidationError as ModelError, ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import FileResponse
from django.utils import timezone
from openpyxl import Workbook
from rest_framework import decorators, response, serializers
from rest_framework.exceptions import PermissionDenied

from backend import purchase_workspace as service
from backend.models import PurchaseOrder, Partner, Currency, Department, Material, Employee, Uom
from .purchase_views import PurchaseOrderViewSet as BaseOrderViewSet
from .requisition_views import PurchaseRequisitionViewSet as BaseRequisitionViewSet, PurchaseOrderLineViewSet as BaseLineViewSet
from .api_common import ErpRolePermission
from .exports import safe_text


def errors(fn):
    @wraps(fn)
    def call(*args, **kwargs):
        try: return fn(*args, **kwargs)
        except ModelError as exc: raise serializers.ValidationError(exc.messages) from exc
        except (ObjectDoesNotExist, ValueError, TypeError, KeyError) as exc:
            raise serializers.ValidationError('资料不存在或参数无效，请重新选择') from exc
        except ProtectedError as exc: raise serializers.ValidationError('单据已有下游引用，不能删除') from exc
        except IntegrityError as exc: raise serializers.ValidationError('单号/生成请求重复，请刷新后重试') from exc
    return call


def purchase_permission(request, action):
    class Target:
        basename='purchase-order'
    view=Target();view.action=action
    if not ErpRolePermission().has_permission(request,view): raise PermissionDenied('没有采购单操作权限')


class PurchaseRequisitionViewSet(BaseRequisitionViewSet):
    @decorators.action(detail=False, methods=['get'], url_path='purchase-candidates')
    @errors
    def purchase_candidates(self,request):
        return response.Response(service.candidates(request.query_params))

    @decorators.action(detail=False, methods=['post'], url_path='purchase-preview')
    @errors
    def purchase_preview(self,request):
        purchase_permission(request,'create')
        return response.Response(service.prepare(request.data))

    @decorators.action(detail=False, methods=['post'], url_path='purchase-generate')
    @errors
    def purchase_generate(self,request):
        purchase_permission(request,'create')
        orders,reused=service.generate(request.data,request.user.get_username())
        return response.Response({'orders':orders,'reused':reused},status=200 if reused else 201)

    @decorators.action(detail=True, methods=['post'], url_path='convert-purchase')
    @errors
    def convert_purchase(self,request,pk=None):
        # Compatibility endpoint funnels old clients through the same allocation service.
        purchase_permission(request,'create')
        doc=self.get_object()
        data=dict(request.data)
        ids=set(doc.lines.values_list('pk',flat=True))
        if any(r.get('line_id') not in ids for r in data.get('lines',[])): raise ModelError('明细不属于当前请购单')
        data.update(supplier=data.get('supplier_id'),department=data.get('department_id'),consider_pack=False,grouping='1')
        data['fingerprint']=service.prepare(data)['fingerprint']
        import uuid
        data['idempotency_key']=request.headers.get('Idempotency-Key') or str(uuid.uuid4())
        orders,_=service.generate(data,request.user.get_username())
        return response.Response(orders[0],status=201)


class PurchaseOrderViewSet(BaseOrderViewSet):
    @errors
    def list(self,request,*args,**kwargs):
        if request.query_params.get('workspace')!='1': return super().list(request,*args,**kwargs)
        qs=self.get_queryset().select_related('supplier','currency','department')
        if request.query_params.get('q'):
            q=request.query_params['q'];qs=qs.filter(Q(number__icontains=q)|Q(supplier__name__icontains=q)|Q(supplier__code__icontains=q))
        if request.query_params.get('status'): qs=qs.filter(status=request.query_params['status'])
        page=max(1,int(request.query_params.get('page',1)));count=qs.count()
        return response.Response(dict(count=count,page=page,results=[dict(id=o.pk,number=o.number,supplier_name=o.supplier.name,
            currency_code=o.currency.code,department_name=o.department.name if o.department_id else "",order_date=str(o.order_date),status=o.status)
            for o in qs.order_by('-order_date','-pk')[(page-1)*50:page*50]]))

    def retrieve(self,request,*args,**kwargs):
        return response.Response(service.order_data(self.get_object()))

    @errors
    def create(self,request,*args,**kwargs):
        if 'lines' not in request.data:
            forbidden={'delivery_approved_by','delivery_approved_at','high_price_permission','version','is_confirmed','confirmed_by','confirmed_at'}
            if forbidden.intersection(request.data): raise ModelError('审批和版本字段由系统维护')
            return super().create(request,*args,**kwargs)
        return response.Response(service.save_order(request.data,request.user.get_username()),status=201)

    @errors
    def update(self,request,*args,**kwargs):
        self.get_object()
        if 'lines' not in request.data:
            raise ModelError('请通过采购单维护页保存完整明细及版本')
        return response.Response(service.save_order(request.data,request.user.get_username(),kwargs['pk']))

    @errors
    @transaction.atomic
    def destroy(self,request,*args,**kwargs):
        obj=PurchaseOrder.objects.select_for_update().get(pk=self.get_object().pk)
        service.editable(obj);service.audit(obj,'delete',request.user.get_username());obj.delete()
        return response.Response(status=204)

    @errors
    @transaction.atomic
    def transition(self,obj,action,actor='',reason=''):
        obj=PurchaseOrder.objects.select_for_update().get(pk=obj.pk)
        if action not in ('submit','approve','unapprove','reject','confirm','unconfirm','void','restore'):
            raise ModelError('采购单不支持此审批操作')
        if action in ('void','restore'): raise ModelError('采购单请通过反审核及删除处理，避免释放错误来源数量')
        if action=='unapprove' and (obj.lines.filter(Q(receipt_lines__isnull=False)|Q(return_lines__isnull=False)).exists() or obj.is_confirmed or obj.delivery_approved_at):
            raise ModelError('已有下游单据或确认/交期审核，不能反审核')
        if action=='approve' and obj.status in ('draft','rejected'): obj.submit()
        if action=='approve':
            if not obj.payment_method: raise ModelError('支付方式不能为空')
            obj.full_clean()
            for line in obj.lines.all():
                if line.allocation_managed and line.allocations.exists():
                    if sum(a.quantity for a in line.allocations.all())!=line.quantity: raise ModelError('来源分配数量不平')
        if action in ('confirm','unconfirm'):
            if action=='confirm':
                if obj.is_confirmed: raise ModelError('已总监确认')
                if not obj.lines.exists(): raise ModelError('请先保存明细')
                obj.is_confirmed=True;obj.confirmed_by=actor;obj.confirmed_at=timezone.now()
            else: obj.is_confirmed=False;obj.confirmed_by='';obj.confirmed_at=None
            obj.version+=1;obj.save();service.audit(obj,action,actor or self.request.user.get_username())
        else:
            super().transition(obj,action,actor,reason)
            obj.refresh_from_db();obj.version+=1;obj.save(update_fields=['version'])
        return response.Response(service.order_data(obj))

    @decorators.action(detail=True,methods=['post'],url_path='delivery-approve')
    @errors
    @transaction.atomic
    def delivery_approve(self,request,pk=None):
        return self._delivery(request,True)

    @decorators.action(detail=True,methods=['post'],url_path='delivery-unapprove')
    @errors
    @transaction.atomic
    def delivery_unapprove(self,request,pk=None):
        return self._delivery(request,False)

    def _delivery(self,request,approve):
        obj=PurchaseOrder.objects.select_for_update().get(pk=self.get_object().pk)
        if obj.status!='approved': raise ModelError('采购审核后才能进行交期审核')
        if approve and obj.delivery_approved_at: raise ModelError('已经交期审核')
        if not approve and not obj.delivery_approved_at: raise ModelError('尚未交期审核')
        obj.delivery_approved_by=request.user.get_username() if approve else ''
        obj.delivery_approved_at=timezone.now() if approve else None
        obj.version+=1;obj.save();service.audit(obj,'delivery_approve' if approve else 'delivery_unapprove',request.user.get_username())
        return response.Response(service.order_data(obj))

    @decorators.action(detail=False,methods=['get'])
    @errors
    def lookups(self,request):
        kind=request.query_params.get('kind','supplier');q=request.query_params.get('q','')
        models={'supplier':Partner,'currency':Currency,'department':Department,'material':Material,'employee':Employee,'uom':Uom}
        if kind not in models: raise ModelError('检索类型无效')
        qs=models[kind].objects.filter(Q(code__icontains=q)|Q(name__icontains=q))
        if kind=='supplier': qs=qs.filter(kind__in=['supplier','both'],status='approved').select_related('currency')
        if kind=='material': qs=qs.filter(status='approved',active=True).select_related('uom','category')
        rows=[]
        for item in qs.order_by('code')[:50]:
            row=dict(id=item.pk,code=item.code,name=item.name)
            if kind=='supplier': row.update(currency=item.currency_id,currency_code=item.currency.code if item.currency_id else '',tax_rate=str(item.tax_rate),payment_method=item.payment_method)
            if kind=='material': row.update(service.material_values(item),uom=item.uom_id,uom_name=item.uom.name)
            rows.append(row)
        return response.Response(rows)

    @decorators.action(detail=True,methods=['get'])
    def export(self,request,pk=None):
        from backend.purchase_columns import ORDER_COLUMNS, ALLOCATION_COLUMNS
        obj=self.get_object();data=service.order_data(obj);wb=Workbook();ws=wb.active;ws.title='采购明细'
        ws.append(['采购单号',obj.number,'供应商',obj.supplier.name,'币种',obj.currency.code])
        ws.append([label for key,label in ORDER_COLUMNS])
        for row in data['lines']: ws.append([safe_text(str(row.get(key,''))) for key,label in ORDER_COLUMNS])
        ws.freeze_panes='D3';ws.auto_filter.ref=ws.dimensions
        detail=wb.create_sheet('关联请购明细');detail.append(['采购行']+[label for key,label in ALLOCATION_COLUMNS])
        for row in data['lines']:
            for a in row['allocations']: detail.append([row['line_number']]+[safe_text(str(a.get(key,''))) for key,label in ALLOCATION_COLUMNS])
        stream=BytesIO();wb.save(stream);stream.seek(0)
        return FileResponse(stream,as_attachment=True,filename=f'{obj.number}.xlsx')


class PurchaseOrderLineViewSet(BaseLineViewSet):
    def perform_create(self,serializer):
        if serializer.validated_data['order'].lines.filter(allocation_managed=True).exists():
            raise serializers.ValidationError('请通过采购单维护页增加明细')
        return super().perform_create(serializer)

    def perform_update(self,serializer):
        if serializer.instance.allocation_managed: raise serializers.ValidationError('请通过采购单维护页同时修改来源分配')
        return super().perform_update(serializer)

    def destroy(self,request,*args,**kwargs):
        if self.get_object().allocation_managed: raise serializers.ValidationError('请通过采购单维护页删除明细')
        return super().destroy(request,*args,**kwargs)
