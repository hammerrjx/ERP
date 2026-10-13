from decimal import Decimal

from django.core.exceptions import ValidationError as ModelError
from django.db import transaction
from django.utils import timezone
from rest_framework import decorators, response, serializers, viewsets

from backend.domain.base import AuditEvent
from backend.domain.inventory import StockBalance, StockTransaction
from backend.domain.master_data import Location
from backend.domain.warehouse_documents import InventoryDictionary, InventoryDocument, InventoryDocumentLine, LegacyInventoryRecord
from backend.inventory_codes import COUNT_ADJUSTMENT, PLAN_ISSUE, PLAN_RECEIPT, TRANSFER_IN, TRANSFER_OUT
from .api_common import ErpRolePermission
from .serializers.common import serializer_for


class WarehouseLineSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    batch_number = serializers.CharField(max_length=18, required=False, allow_blank=True)
    grade = serializers.CharField(max_length=2, required=False, allow_blank=True)
    material_code = serializers.CharField(source="material.code", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    specification = serializers.CharField(source="material.specification", read_only=True)
    english_name = serializers.CharField(source="material.english_name", read_only=True)

    class Meta:
        model = InventoryDocumentLine
        exclude = ("document",)
        read_only_fields = ("uom", "system_quantity", "variance_quantity", "created_by", "created_at",
                            "modification_count", "modified_by", "modified_at")

    def validate(self, attrs):
        attrs["uom"] = attrs["material"].uom
        return attrs


def validate_lines(kind, head, lines):
    if not lines:
        raise serializers.ValidationError("至少填写一条明细")
    numbers = set()
    stock_keys = set()
    for line in lines:
        number = line["line_number"]
        if number <= 0 or number in numbers:
            raise serializers.ValidationError("行号须为不重复的正整数")
        numbers.add(number)
        material = line["material"]
        if line["uom"].pk != material.uom_id:
            raise serializers.ValidationError("库存单据使用物料库存基本单位")
        if material.no_stock_movement or not material.active:
            raise serializers.ValidationError("物料已停用或不参与库存移动")
        if material.batch_control and not line.get("batch_number"):
            raise serializers.ValidationError("批号控制物料必须填写批号")
        src = line.get("from_location") or head.get("from_location")
        dst = line.get("to_location") or head.get("to_location")
        if kind in {"transfer", "scrap", "issue", "count"} and not src:
            raise serializers.ValidationError("出库/盘点库位必填")
        if kind in {"transfer", "scrap", "receipt", "opening"} and not dst:
            raise serializers.ValidationError("入库库位必填")
        if kind in {"transfer", "scrap"}:
            if src.pk == dst.pk:
                raise serializers.ValidationError("出入库位不能相同")
            if src.source_site != dst.source_site:
                raise serializers.ValidationError("首期不支持跨站点转仓")
        if kind == "scrap" and not (dst.code.startswith("SCR") or dst.location_attribute == "SCR"):
            raise serializers.ValidationError("报废目的库位必须为报废库；恢复请通过原单冲销")
        if kind == "count":
            if not head.get("from_location") or src.pk != head["from_location"].pk:
                raise serializers.ValidationError("盘点明细必须属于单头盘点库位")
            key = (material.pk, src.pk, line.get("batch_number", ""))
            if key in stock_keys:
                raise serializers.ValidationError("同一物料库位批号不能重复盘点")
            stock_keys.add(key)
            counted = line.get("counted_quantity")
            if counted is not None and counted < 0:
                raise serializers.ValidationError("实盘数量不能为负数")
        elif line.get("quantity", Decimal(0)) <= 0:
            raise serializers.ValidationError("数量必须大于零，冲回请使用原单冲销")
        for loc in (src, dst):
            if loc and loc.disabled_for_inventory:
                raise serializers.ValidationError(f"库位 {loc.code} 已停用")
        line["from_location"] = src
        line["to_location"] = dst


class WarehouseSerializer(serializers.ModelSerializer):
    lines = WarehouseLineSerializer(many=True)
    checker_code = serializers.CharField(source="checker.code", read_only=True)
    checker_name = serializers.CharField(source="checker.name", read_only=True)

    class Meta:
        model = InventoryDocument
        fields = "__all__"
        read_only_fields = ("number", "status", "created_by", "created_at", "updated_at", "confirmed_by", "confirmed_at",
                            "posted_by", "posted_at", "reversed_by", "reversed_at", "reversal_reason", "source_key", "source_payload")

    def validate(self, attrs):
        if self.instance:
            if self.instance.status != "draft" or self.instance.source_key:
                raise serializers.ValidationError("已确认、已过账或导入单据不可修改")
            if attrs.get("kind", self.instance.kind) != self.instance.kind:
                raise serializers.ValidationError("单据类型不可更改")
        kind = attrs.get("kind", getattr(self.instance, "kind", None))
        if kind == "transfer":
            transfer_class = attrs.get("transfer_class", getattr(self.instance, "transfer_class", "")) or "1"
            if transfer_class not in {"1", "2", "3"}:
                raise serializers.ValidationError({"transfer_class": "请选择内部转仓、外协领料转仓或外协退料转仓"})
            attrs["transfer_class"] = transfer_class
        checker = attrs.get("checker", getattr(self.instance, "checker", None))
        if kind == "count":
            if checker is None:
                raise serializers.ValidationError({"checker": "盘点人必填"})
            if checker.is_locked or checker.is_left:
                raise serializers.ValidationError({"checker": "锁定或出差/请假用户不可作为盘点人"})
        category = attrs.get("category_code", getattr(self.instance, "category_code", ""))
        if category and not InventoryDictionary.objects.filter(dictionary="MOV_CAT", code=category, disabled=False).exists():
            raise serializers.ValidationError("业务类型不在有效源库字典中")
        if kind == "receipt" and category == "001":
            for line in attrs.get("lines", []):
                if line.get("reference_cost") is None or line["reference_cost"] < 0:
                    raise serializers.ValidationError("初盘入库须填写非负参考单位成本，零成本请明确填写 0")
        supplier = attrs.get("supplier", getattr(self.instance, "supplier", None))
        if supplier and supplier.kind not in {"supplier", "both"}:
            raise serializers.ValidationError("外协供应商必须来自供应商资料")
        if kind == "opening":
            raise serializers.ValidationError("期初仅由受控导入创建")
        head = {name: attrs.get(name, getattr(self.instance, name, None)) for name in ("from_location", "to_location")}
        if "lines" not in attrs:
            raise serializers.ValidationError("保存单据须提供完整明细")
        existing = {line.pk: line for line in self.instance.lines.all()} if self.instance else {}
        seen_ids = set()
        for line in attrs["lines"]:
            line_id = line.get("id")
            if line_id is not None:
                if line_id not in existing or line_id in seen_ids:
                    raise serializers.ValidationError("明细 ID 不属于当前单据或重复")
                if existing[line_id].line_number != line["line_number"]:
                    raise serializers.ValidationError("已有明细的行号不可修改")
                seen_ids.add(line_id)
        validate_lines(kind, head, attrs["lines"])
        return attrs

    def create(self, data):
        lines = data.pop("lines")
        doc = InventoryDocument.objects.create(**data)
        for line in lines:
            InventoryDocumentLine.objects.create(document=doc, created_by=doc.created_by, created_at=timezone.now(), **line)
        return doc

    def update(self, doc, data):
        lines = data.pop("lines")
        for name, value in data.items():
            setattr(doc, name, value)
        doc.save()
        existing = {line.line_number: line for line in doc.lines.all()}
        kept = []
        actor = self.context["request"].user.get_username()
        for line in lines:
            line.pop("id", None)
            current = existing.get(line["line_number"])
            if current is None:
                current = InventoryDocumentLine.objects.create(document=doc, created_by=actor, created_at=timezone.now(), **line)
            elif any(getattr(current, name) != value for name, value in line.items()):
                for name, value in line.items():
                    setattr(current, name, value)
                current.modification_count += 1
                current.modified_by, current.modified_at = actor, timezone.now()
                current.save()
            kept.append(current.pk)
        doc.lines.exclude(pk__in=kept).delete()
        return doc


class InventoryDocumentViewSet(viewsets.ModelViewSet):
    queryset = InventoryDocument.objects.select_related('checker').prefetch_related("lines__material", "lines__uom").all()
    serializer_class = WarehouseSerializer
    permission_classes = (ErpRolePermission,)
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        kind = self.request.query_params.get("kind")
        return qs.filter(kind=kind) if kind else qs

    def list(self, request, *args, **kwargs):
        if request.query_params.get('summary') == '1':
            qs = self.get_queryset()
            if request.query_params.get('category'):
                qs = qs.filter(category_code=request.query_params['category'])
            return response.Response(list(qs.values('id', 'number', 'document_date', 'status',
                'from_location', 'to_location', 'notes', 'category_code')))
        return super().list(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        doc = serializer.save(created_by=self.request.user.get_username())
        self.audit(doc, "create")

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        InventoryDocument.objects.select_for_update().get(pk=kwargs["pk"])
        result = super().update(request, *args, **kwargs)
        self.audit(self.get_object(), "update")
        return result

    @transaction.atomic
    def perform_destroy(self, obj):
        obj = InventoryDocument.objects.select_for_update().get(pk=obj.pk)
        if obj.status != "draft" or obj.source_key:
            raise serializers.ValidationError("只有未确认的本地草稿可删除")
        self.audit(obj, "delete")
        obj.delete()

    def audit(self, doc, action, reason=""):
        AuditEvent.objects.create(model=doc._meta.label_lower, object_id=str(doc.pk), action=action,
                                  actor=self.request.user.get_username(), reason=reason)

    @decorators.action(detail=True, methods=["post"])
    @transaction.atomic
    def transition(self, request, pk=None):
        doc = InventoryDocument.objects.select_for_update().get(pk=self.get_object().pk)
        action = request.data.get("action")
        actor = request.user.get_username()
        if doc.source_key:
            raise serializers.ValidationError("导入单据只读，不允许重复过账")
        if action == "approve" and doc.status == "posted" or action == "reverse" and doc.status == "reversed":
            return response.Response(self.get_serializer(doc).data)
        if action == "approve":
            opening = InventoryDocument.objects.filter(kind="opening", status="posted").order_by("-document_date").first()
            if opening and doc.document_date < opening.document_date:
                raise serializers.ValidationError("业务日期不能早于试点期初日期")
        lines = list(doc.lines.select_related("material", "uom", "from_location", "to_location"))
        location_ids = sorted({loc for line in lines for loc in (line.from_location_id, line.to_location_id) if loc})
        list(Location.objects.select_for_update().filter(pk__in=location_ids).order_by("pk"))
        if action == "confirm" and doc.status == "draft" and doc.kind in {"transfer", "count"}:
            if doc.kind == "count":
                if doc.count_basis != "2":
                    raise serializers.ValidationError("盘点日期实时库存/单据库存取数规则尚未核验，请使用即时库存")
                if InventoryDocument.objects.filter(kind="count", status="confirmed", from_location=doc.from_location).exclude(pk=doc.pk).exists():
                    raise serializers.ValidationError("该库位已有进行中的盘点")
                for line in lines:
                    balance = StockBalance.objects.filter(material=line.material, location=line.from_location, batch_number=line.batch_number).first()
                    line.system_quantity = balance.quantity if balance else Decimal(0)
                    line.variance_quantity = None
                    line.save(update_fields=["system_quantity", "variance_quantity"])
            doc.status, doc.confirmed_by, doc.confirmed_at = "confirmed", actor, timezone.now()
        elif action == "unconfirm" and doc.status == "confirmed":
            doc.status, doc.confirmed_by, doc.confirmed_at = "draft", "", None
        elif action == "count-results" and doc.kind == "count" and doc.status == "confirmed":
            values = request.data.get("results", {})
            if set(values) != {str(line.pk) for line in lines}:
                raise serializers.ValidationError("请提交所有盘点行的实盘数量")
            field = serializers.DecimalField(max_digits=20, decimal_places=8, min_value=Decimal(0))
            for line in lines:
                counted = field.run_validation(values[str(line.pk)])
                if counted != line.counted_quantity:
                    line.modification_count += 1
                    line.modified_by, line.modified_at = actor, timezone.now()
                line.counted_quantity = counted
                line.variance_quantity = line.counted_quantity - line.system_quantity
                line.save(update_fields=["counted_quantity", "variance_quantity", "modification_count", "modified_by", "modified_at"])
        elif action == "approve" and doc.status == ("confirmed" if doc.kind in {"transfer", "count"} else "draft"):
            validate_lines(doc.kind, {"from_location": doc.from_location, "to_location": doc.to_location}, [
                {f.name: getattr(line, f.name) for f in line._meta.fields if f.name not in {"id", "document"}} for line in lines
            ])
            try:
                for line in lines:
                    common = dict(material=line.material, uom=line.uom, batch_number=line.batch_number,
                                  source_model=doc._meta.label_lower, source_id=doc.pk, source_line_id=line.pk,
                                  actor=actor, effective_date=doc.document_date)
                    movements = []
                    if doc.kind in {"transfer", "scrap"}:
                        movements = [(line.from_location, -line.quantity, TRANSFER_OUT), (line.to_location, line.quantity, TRANSFER_IN)]
                    elif doc.kind == "receipt":
                        movements = [(line.to_location, line.quantity, PLAN_RECEIPT)]
                    elif doc.kind == "issue":
                        movements = [(line.from_location, -line.quantity, PLAN_ISSUE)]
                    elif doc.kind == "count":
                        if line.system_quantity is None or line.counted_quantity is None:
                            raise serializers.ValidationError("请登记全部实盘数量")
                        delta = line.counted_quantity - line.system_quantity
                        if delta:
                            movements = [(line.from_location, delta, COUNT_ADJUSTMENT)]
                        line.variance_quantity = delta
                        line.save(update_fields=["variance_quantity"])
                    for location, quantity, movement in movements:
                        StockBalance.adjust(location=location, quantity=quantity, movement_type=movement, **common)
            except ModelError as exc:
                raise serializers.ValidationError(exc.messages) from exc
            doc.status, doc.posted_by, doc.posted_at = "posted", actor, timezone.now()
        elif action == "reverse" and doc.status == "posted":
            reason = str(request.data.get("reason", "")).strip()
            if not reason or len(reason) > 240:
                raise serializers.ValidationError("冲销原因必填，最多240字")
            originals = StockTransaction.objects.filter(source_model=doc._meta.label_lower, source_id=str(doc.pk), reversal_of__isnull=True).order_by("-pk")
            try:
                for original in originals:
                    StockBalance.adjust(material=original.material, location=original.location, uom=original.uom,
                        # Keep the business category while retaining our append-only
                        # reversal audit trail and opposite signed quantity.
                        quantity=-original.quantity, movement_type=original.movement_type, source_model=doc._meta.label_lower,
                        source_id=doc.pk, source_line_id=f"R{original.pk}", actor=actor,
                        batch_number=original.batch_number, reversal_of=original)
            except ModelError as exc:
                raise serializers.ValidationError(exc.messages) from exc
            doc.status, doc.reversed_by, doc.reversed_at = "reversed", actor, timezone.now()
            doc.reversal_reason = reason
        else:
            raise serializers.ValidationError("当前单据状态不允许此操作")
        doc.save()
        self.audit(doc, action, doc.reversal_reason)
        return response.Response(self.get_serializer(doc).data)


class LegacyInventoryRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LegacyInventoryRecord.objects.order_by("-effective_date", "-id")
    serializer_class = serializer_for(LegacyInventoryRecord)
    permission_classes = (ErpRolePermission,)


class InventoryDictionaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryDictionary.objects.all()
    serializer_class = serializer_for(InventoryDictionary)
    permission_classes = (ErpRolePermission,)
