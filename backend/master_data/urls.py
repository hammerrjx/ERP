from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from backend.importing.views import MaterialImportConfirmView, MaterialImportDetailView, MaterialImportPreviewView

router = DefaultRouter()
for resource in (
    "business_group", "company", "currency", "currency_rate", "customer_material", "customer_address", "document_evidence", "location",
    "material", "material_company", "material_uom_conversion", "partner", "payment_method", "tax_code",
    "partner_bank_account", "partner_company", "partner_contact", "product_category",
    "supplier_quote", "supplier_quote_line", "uom", "uom_category", "audit_event",
    "department", "role", "user_role", "approval_rule", "user_account", "employee", "bom",
    "bom_line", "routing", "routing_operation", "warehouse", "sales_quote",
    "sales_quote_line", "sales_order", "sales_order_line", "purchase_requisition",
    "purchase_requisition_line", "rfq", "rfq_line", "supplier_inquiry",
    "purchase_order", "purchase_order_line", "goods_receipt", "goods_receipt_line",
    "payable_voucher", "payable_voucher_line",
    "stock_balance", "stock_transaction", "delivery_order", "delivery_order_line",
    "stock_transfer", "stock_transfer_line", "stock_count", "stock_count_line",
    "inventory_alert", "purchase_return", "purchase_return_line", "sales_return",
    "sales_return_line",
):
    prefix = resource.replace("_", "-")
    router.register(prefix, getattr(views, "".join(part.title() for part in resource.split("_")) + "ViewSet"), basename=prefix)

urlpatterns = [
    path("material-import/preview/", MaterialImportPreviewView.as_view()),
    path("material-import/<int:pk>/", MaterialImportDetailView.as_view()),
    path("material-import/<int:pk>/confirm/", MaterialImportConfirmView.as_view()),
] + router.urls
