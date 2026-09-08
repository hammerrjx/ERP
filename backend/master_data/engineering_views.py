from backend.domain.engineering import BillOfMaterial, BomLine, Routing, RoutingOperation
from .serializers.common import serializer_for
from .api_common import make_viewset


BomViewSet = make_viewset(BillOfMaterial, serializer_for(BillOfMaterial))
BomLineViewSet = make_viewset(BomLine, serializer_for(BomLine))
RoutingViewSet = make_viewset(Routing, serializer_for(Routing))
RoutingOperationViewSet = make_viewset(RoutingOperation, serializer_for(RoutingOperation))
