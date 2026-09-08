from backend.models import BillOfMaterial, BomLine, Routing, RoutingOperation

from .common import serializer_for

BillOfMaterialSerializer = serializer_for(BillOfMaterial)


BomLineSerializer = serializer_for(BomLine)


RoutingSerializer = serializer_for(Routing)


RoutingOperationSerializer = serializer_for(RoutingOperation)
