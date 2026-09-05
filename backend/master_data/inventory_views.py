from rest_framework import response, viewsets

from backend.domain.inventory import StockBalance, StockCount, StockCountLine, StockTransaction, StockTransfer, StockTransferLine
from .api_common import ErpRolePermission, make_viewset
from .serializers import (
    StockBalanceSerializer, StockCountLineSerializer, StockCountSerializer,
    StockTransactionSerializer, StockTransferLineSerializer, StockTransferSerializer,
)

StockBalanceViewSet = make_viewset(StockBalance, StockBalanceSerializer)
StockTransactionViewSet = make_viewset(StockTransaction, StockTransactionSerializer)
StockTransferViewSet = make_viewset(StockTransfer, StockTransferSerializer)
StockTransferLineViewSet = make_viewset(StockTransferLine, StockTransferLineSerializer)
StockCountViewSet = make_viewset(StockCount, StockCountSerializer)
StockCountLineViewSet = make_viewset(StockCountLine, StockCountLineSerializer)


class InventoryAlertViewSet(viewsets.ViewSet):
    queryset = StockBalance.objects.none()
    permission_classes = (ErpRolePermission,)

    def list(self, request):
        alerts = []
        balances = StockBalance.objects.select_related("material", "location", "uom")
        for balance in balances:
            threshold = balance.material.stock_warning_qty
            if threshold > 0 and balance.quantity < threshold:
                alerts.append({
                    "material": balance.material_id,
                    "material_code": balance.material.code,
                    "material_name": balance.material.name,
                    "location": balance.location_id,
                    "location_code": balance.location.code,
                    "uom": balance.uom_id,
                    "quantity": f"{balance.quantity:.6f}",
                    "warning_quantity": f"{threshold:.6f}",
                    "shortage_quantity": f"{threshold - balance.quantity:.6f}",
                })
        return response.Response(alerts)
