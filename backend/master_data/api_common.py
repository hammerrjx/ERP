from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.db import transaction
from rest_framework import decorators, permissions, response, serializers, viewsets

from backend.domain.system import ApprovalStatus, AuditEvent, UserRole
from backend.models import DocumentEvidence
from .exports import definition_for, export_queryset, workbook_response


def _has_status_field(model):
    return any(field.name == "status" for field in model._meta.get_fields())


def _approved_owner(obj, seen=None):
    """Find an approved document through the object's CASCADE parent chain."""
    if obj is None:
        return None
    seen = set() if seen is None else seen
    marker = (obj.__class__, getattr(obj, "pk", None) or id(obj))
    if marker in seen:
        return None
    seen.add(marker)
    if _has_status_field(obj.__class__) and (getattr(obj, "status", None) == ApprovalStatus.APPROVED
            or (obj._meta.model_name in {"deliveryorder", "salesreturn"} and obj.posted)):
        return obj
    for field in obj._meta.get_fields():
        if not getattr(field, "many_to_one", False) or field.remote_field.on_delete is not models.CASCADE:
            continue
        parent = getattr(obj, field.name, None)
        owner = _approved_owner(parent, seen)
        if owner is not None:
            return owner
    return None


def ensure_editable(obj):
    owner = _approved_owner(obj)
    if owner is not None:
        raise serializers.ValidationError("已审核资料不可修改，请先由具备反审核权限的账号反审核")


def ensure_editable_data(data):
    for value in data.values():
        if hasattr(value, "_meta"):
            ensure_editable(value)


def ensure_status_unchanged(serializer):
    if "status" in serializer.validated_data and serializer.validated_data["status"] != serializer.instance.status:
        raise serializers.ValidationError("审核状态只能通过提交、审核或反审核动作变更")


class ErpRolePermission(permissions.BasePermission):
    parent_resources = {
        "bom_line": "bom", "routing_operation": "routing",
        "sales_quote_line": "sales_quote", "sales_order_line": "sales_order",
        "supplier_quote_line": "supplier_quote",
        "purchase_requisition_line": "purchase_requisition", "rfq_line": "rfq",
        "supplier_inquiry": "rfq", "purchase_order_line": "purchase_order",
        "goods_receipt_line": "goods_receipt", "delivery_order_line": "delivery_order",
        "payable_voucher_line": "payable_voucher",
        "stock_transfer_line": "stock_transfer", "stock_count_line": "stock_count",
        "purchase_return_line": "purchase_return", "sales_return_line": "sales_return",
    }
    action_permissions = {
        "list": "view", "retrieve": "view", "create": "create",
        "update": "change", "partial_update": "change", "destroy": "delete",
        "submit": "submit", "approve": "approve", "reject": "approve",
        "unapprove": "approve", "confirm": "approve", "unconfirm": "approve",
        "ratify": "ratify", "unratify": "ratify",
        "sales_confirm": "approve", "sales_unconfirm": "approve",
        "void": "delete", "restore": "change", "convert": "create",
        "auto_generate": "create", "generate_requisition": "create",
        "generate_from_order": "create", "generate_receipt": "create",
        "reserve_number": "create", "save_sheet": "create", "update_sheet": "change", "order_candidates": "view",
        "delivery_approve": "approve", "delivery_unapprove": "approve",
        "po_change_confirm": "approve", "po_change_unconfirm": "approve", "print": "view",
        "export": "view",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        action = self.action_permissions.get(getattr(view, "action", ""), "view")
        resource = getattr(view, "basename", "").replace("-", "_")
        resource = self.parent_resources.get(resource, resource)
        if resource == "sales_quote" and getattr(view, "action", "") in {"confirm", "unconfirm"}:
            action = "confirm"
        required = f"{resource}.{action}"
        assignments = UserRole.objects.filter(
            user=user, active=True, role__active=True, role__status=ApprovalStatus.APPROVED,
        ).values_list("role__permissions", flat=True)
        return any("*" in values or required in values for values in assignments)


class ApprovalViewSet(viewsets.ModelViewSet):
    permission_classes = (ErpRolePermission,)

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user.get_username())
        AuditEvent.objects.create(
            model=obj._meta.label_lower,
            object_id=str(obj.pk),
            action="create",
            actor=self.request.user.get_username() or "system",
        )

    def perform_update(self, serializer):
        ensure_editable(serializer.instance)
        ensure_status_unchanged(serializer)
        obj = serializer.save(updated_by=self.request.user.get_username())
        AuditEvent.objects.create(
            model=obj._meta.label_lower,
            object_id=str(obj.pk),
            action="update",
            actor=self.request.user.get_username() or "system",
        )

    @transaction.atomic
    def transition(self, obj, action, actor="", reason=""):
        if obj._meta.model_name in {"deliveryorder", "salesreturn", "salesorder"}:
            obj = type(obj).objects.select_for_update().get(pk=obj.pk)
        if obj._meta.model_name in {"deliveryorder", "salesreturn"} and obj.posted:
            if action == "approve" and obj.status == ApprovalStatus.APPROVED:
                return response.Response(self.get_serializer(obj).data)
            if action not in {"confirm", "unconfirm"}:
                raise serializers.ValidationError("已生效单据只能登记回单或通过退货、红冲纠正")
        try:
            if action == "approve":
                obj.approve(actor)
            elif action == "reject":
                obj.reject(actor, reason)
            elif action == "confirm":
                if obj._meta.model_name == "goodsreceipt" and not obj.supplier_delivery_number:
                    raise serializers.ValidationError("确认收货前必须填写供应商送货单号")
                evidence_type = {
                    "goodsreceipt": DocumentEvidence.EvidenceType.SUPPLIER_DELIVERY,
                    "deliveryorder": DocumentEvidence.EvidenceType.CUSTOMER_DELIVERY,
                    "salesreturn": DocumentEvidence.EvidenceType.CUSTOMER_RETURN,
                    "purchasereturn": DocumentEvidence.EvidenceType.WAREHOUSE_RETURN,
                }.get(obj._meta.model_name)
                if evidence_type and not DocumentEvidence.objects.filter(
                    document_type=obj._meta.model_name,
                    document_id=obj.pk,
                    evidence_type=evidence_type,
                ).exists():
                    raise serializers.ValidationError("确认前必须上传签收/退货凭证")
                obj.confirm(actor)
            elif action == "ratify":
                obj.ratify(actor)
            elif action == "sales_confirm":
                obj.sales_confirm(actor)
            elif action == "sales_unconfirm":
                obj.sales_unconfirm()
            else:
                getattr(obj, action)()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        obj.save()
        AuditEvent.objects.create(
            model=obj._meta.label_lower,
            object_id=str(obj.pk),
            action=action,
            actor=actor or "system",
            reason=reason,
        )
        return response.Response(self.get_serializer(obj).data)

    def destroy(self, request, *args, **kwargs):
        ensure_editable(self.get_object())
        return super().destroy(request, *args, **kwargs)

    @decorators.action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        return self.transition(self.get_object(), "submit")

    @decorators.action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        actor = request.user.get_username() or "system"
        return self.transition(self.get_object(), "approve", actor)

    @decorators.action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        actor = request.user.get_username() or "system"
        return self.transition(self.get_object(), "reject", actor, request.data.get("reason", ""))

    @decorators.action(detail=True, methods=["post"])
    def unapprove(self, request, pk=None):
        return self.transition(self.get_object(), "unapprove")

    @decorators.action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        actor = request.user.get_username() or "system"
        return self.transition(self.get_object(), "confirm", actor)

    @decorators.action(detail=True, methods=["post"])
    def unconfirm(self, request, pk=None):
        return self.transition(self.get_object(), "unconfirm")

    @decorators.action(detail=True, methods=["post"])
    def ratify(self, request, pk=None):
        return self.transition(self.get_object(), "ratify", request.user.get_username() or "system")

    @decorators.action(detail=True, methods=["post"])
    def unratify(self, request, pk=None):
        return self.transition(self.get_object(), "unratify")

    @decorators.action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        return self.transition(self.get_object(), "void")

    @decorators.action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        return self.transition(self.get_object(), "restore")


class EditableViewSet(viewsets.ModelViewSet):
    permission_classes = (ErpRolePermission,)

    def perform_update(self, serializer):
        ensure_editable(serializer.instance)
        ensure_status_unchanged(serializer)
        serializer.save(updated_by=self.request.user.get_username())

    def destroy(self, request, *args, **kwargs):
        ensure_editable(self.get_object())
        return super().destroy(request, *args, **kwargs)


def make_viewset(model, serializer):
    attributes = {
        "queryset": model.objects.all(), "serializer_class": serializer,
        "permission_classes": (ErpRolePermission,),
    }
    if definition_for(model, "customer" if model._meta.model_name == "partner" else None):
        @decorators.action(detail=False, methods=["post"])
        def export(self, request):
            definition, queryset = export_queryset(self.get_queryset(), request)
            return workbook_response(definition, queryset)
        attributes["export"] = export
    return type(f"{model.__name__}ViewSet", (ApprovalViewSet if hasattr(model, "submit") else EditableViewSet,), attributes)
