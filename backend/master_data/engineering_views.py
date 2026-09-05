from backend.domain.engineering import BillOfMaterial, BomLine, Routing, RoutingOperation
from .api_common import make_viewset
from .serializers import BillOfMaterialSerializer, BomLineSerializer, RoutingOperationSerializer, RoutingSerializer

BomViewSet = make_viewset(BillOfMaterial, BillOfMaterialSerializer)
BomLineViewSet = make_viewset(BomLine, BomLineSerializer)
RoutingViewSet = make_viewset(Routing, RoutingSerializer)
RoutingOperationViewSet = make_viewset(RoutingOperation, RoutingOperationSerializer)
