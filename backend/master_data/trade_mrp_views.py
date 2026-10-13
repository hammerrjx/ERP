from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from rest_framework import decorators, response, serializers, viewsets

from backend.domain.trade_mrp import TradeMrpRun, TradeMrpResult, calculate_trade_mrp, confirm_trade_mrp, preview_trade_mrp_generation
from backend.models import CustomerMaterial, Department, Employee


class TradeMrpResultSerializer(serializers.ModelSerializer):
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    uom_name = serializers.CharField(source="uom.name", read_only=True)

    class Meta:
        model = TradeMrpResult
        fields = "__all__"


class TradeMrpRunSerializer(serializers.ModelSerializer):
    results = TradeMrpResultSerializer(many=True, read_only=True)
    generation_enabled = serializers.SerializerMethodField()
    generation_readiness = serializers.SerializerMethodField()

    def get_generation_enabled(self, obj):
        return self.get_generation_readiness(obj)['enabled']

    def get_generation_readiness(self, obj):
        from backend.trade_mrp_readiness import generation_readiness
        return generation_readiness(obj.site)

    class Meta:
        model = TradeMrpRun
        fields = "__all__"


class TradeMrpViewSet(viewsets.GenericViewSet):
    queryset = TradeMrpRun.objects.all().prefetch_related("results__material", "results__uom")
    serializer_class = TradeMrpRunSerializer

    @decorators.action(detail=False, methods=["post"])
    def preview(self, request):
        payload = TradeMrpPreviewSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        values = payload.validated_data
        filters = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in values.items() if k not in {"site", "mode"}}
        try:
            run = calculate_trade_mrp(site=values["site"], mode=values["mode"], filters=filters, actor=request.user.get_username())
        except ValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return response.Response(self.get_serializer(run).data, status=201)

    @decorators.action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        payload = TradeMrpConfirmSerializer(data=request.data, context={'request': request})
        payload.is_valid(raise_exception=True)
        try:
            req = confirm_trade_mrp(pk, actor=request.user.get_username(), **payload.validated_data)
        except (ValidationError, TradeMrpRun.DoesNotExist) as exc:
            raise serializers.ValidationError(str(exc))
        return response.Response({"id": req.pk, "number": req.number, "status": req.status}, status=201)

    @decorators.action(detail=True, methods=["post"], url_path="generation-preview")
    def generation_preview(self, request, pk=None):
        payload = TradeMrpConfirmSerializer(data=request.data, context={'request': request})
        payload.is_valid(raise_exception=True)
        try:
            plan = preview_trade_mrp_generation(pk, **payload.validated_data)
        except (ValidationError, TradeMrpRun.DoesNotExist) as exc:
            raise serializers.ValidationError(str(exc))
        return response.Response(plan)

    @decorators.action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            run = self.get_queryset().select_for_update().get(pk=self.get_object().pk)
            if run.status != 'preview':
                raise serializers.ValidationError('只能取消未确认的分析批次')
            run.status = 'cancelled'
            run.save(update_fields=['status'])
        return response.Response(self.get_serializer(run).data)

    @decorators.action(detail=False, methods=["get"], url_path="customer-materials")
    def customer_materials(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return response.Response([])
        rows = CustomerMaterial.objects.select_related('customer', 'material').filter(enabled=True).filter(
            Q(terminal_customer_code__icontains=q) | Q(customer_code__icontains=q) |
            Q(customer__code__icontains=q) | Q(material__code__icontains=q)).order_by('customer__code', 'material__code', 'customer_code')[:50]
        return response.Response([{'id': r.pk, 'customer': r.customer.code, 'customer_name': r.customer.name,
            'material': r.material.code, 'material_name': r.material.name, 'customer_code': r.customer_code,
            'terminal_code': r.terminal_customer_code} for r in rows])

    def retrieve(self, request, *args, **kwargs):
        return response.Response(self.get_serializer(self.get_object()).data)

    def list(self, request, *args, **kwargs):
        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except ValueError:
            raise serializers.ValidationError('页码必须是整数')
        qs = self.get_queryset()
        if request.query_params.get('site'):
            qs = qs.filter(site=request.query_params['site'])
        if request.query_params.get('status'):
            qs = qs.filter(status=request.query_params['status'])
        return response.Response({'count': qs.count(), 'page': page, 'results': list(qs.values(
            'id', 'site', 'status', 'created_at', 'created_by', 'confirmed_at', 'confirmation_snapshot')[(page-1)*20:page*20])})


class TradeMrpPreviewSerializer(serializers.Serializer):
    site = serializers.CharField(max_length=20, default="1000")
    mode = serializers.ChoiceField(choices=["net"], default="net")
    order = serializers.CharField(max_length=80, allow_blank=True, default="")
    material = serializers.CharField(max_length=160, allow_blank=True, default="")
    customer = serializers.CharField(max_length=160, allow_blank=True, default="")
    customer_po = serializers.CharField(max_length=80, allow_blank=True, default="")
    customer_material_id = serializers.PrimaryKeyRelatedField(queryset=CustomerMaterial.objects.filter(enabled=True), required=False, allow_null=True)
    date_from = serializers.DateField(required=False, allow_null=True)
    date_to = serializers.DateField(required=False, allow_null=True)
    last_pr = serializers.BooleanField(default=True)
    order_from = serializers.CharField(max_length=40, allow_blank=True, required=False)
    order_to = serializers.CharField(max_length=40, allow_blank=True, required=False)
    line_from = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    line_to = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    order_date_from = serializers.DateField(required=False, allow_null=True)
    order_date_to = serializers.DateField(required=False, allow_null=True)
    material_from = serializers.CharField(max_length=40, allow_blank=True, required=False)
    material_to = serializers.CharField(max_length=40, allow_blank=True, required=False)
    category_from = serializers.CharField(max_length=40, allow_blank=True, required=False)
    category_to = serializers.CharField(max_length=40, allow_blank=True, required=False)
    planner = serializers.CharField(max_length=64, allow_blank=True, required=False)
    buyer = serializers.CharField(max_length=64, allow_blank=True, required=False)

    def validate_customer_material_id(self, value):
        return value.pk if value else None


class GenerationHeaderSerializer(serializers.Serializer):
    requester = serializers.CharField(max_length=64, required=False)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False, allow_null=True)
    request_date = serializers.DateField(required=False)
    notes = serializers.CharField(max_length=240, allow_blank=True, default='')

    def validate_requester(self, value):
        if value != self.context['request'].user.get_username() and not Employee.objects.filter(code=value, is_left=False, is_locked=False).exists():
            raise serializers.ValidationError('请购人不存在或已离职/锁定')
        return value

    def validate_department_id(self, value):
        return value.pk if value else None

    def validate_request_date(self, value):
        return value.isoformat()


class TradeMrpConfirmSerializer(serializers.Serializer):
    quantities = serializers.DictField(child=serializers.CharField(), required=False)
    source_quantities = serializers.DictField(child=serializers.CharField(), required=False)
    selected_sources = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False)
    adjustment_reason = serializers.CharField(max_length=1000, allow_blank=True, default="")
    header = GenerationHeaderSerializer(required=False)
