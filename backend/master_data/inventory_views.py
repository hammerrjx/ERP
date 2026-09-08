from rest_framework import response, viewsets

from backend.domain.inventory import (
    StockBalance,
    StockCount,
    StockCountLine,
    StockTransaction,
    StockTransfer,
    StockTransferLine,
)
from .serializers.common import serializer_for
from .api_common import ErpRolePermission, make_viewset


StockBalanceViewSet = make_viewset(StockBalance, serializer_for(StockBalance))
StockTransactionViewSet = make_viewset(StockTransaction, serializer_for(StockTransaction))
StockTransferViewSet = make_viewset(StockTransfer, serializer_for(StockTransfer))
StockTransferLineViewSet = make_viewset(StockTransferLine, serializer_for(StockTransferLine))
StockCountViewSet = make_viewset(StockCount, serializer_for(StockCount))
StockCountLineViewSet = make_viewset(StockCountLine, serializer_for(StockCountLine))


class InventoryAlertViewSet(viewsets.ViewSet):
    queryset = StockBalance.objects.none()
    permission_classes = (ErpRolePermission,)

    def list(self, request):
        alerts = []
        balances = StockBalance.objects.select_related("material", "location", "uom")
        for balance in balances:
            threshold = balance.material.stock_warning_qty
            if threshold > 0 and balance.quantity < threshold:
                alerts.append(
                    {
                        "material": balance.material_id,
                        "material_code": balance.material.code,
                        "material_name": balance.material.name,
                        "location": balance.location_id,
                        "location_code": balance.location.code,
                        "uom": balance.uom_id,
                        "quantity": f"{balance.quantity:.6f}",
                        "warning_quantity": f"{threshold:.6f}",
                        "shortage_quantity": f"{threshold - balance.quantity:.6f}",
                    }
                )
        return response.Response(alerts)
