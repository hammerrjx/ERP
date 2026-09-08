from rest_framework.test import APITestCase

from backend.test_support import ApiSupport


class EngineeringApiTests(ApiSupport, APITestCase):
    def material_context(self, with_component=True):
        uom_category = self.post("uom-category", {"code": "COUNT", "name": "数量"})
        uom = self.post("uom", {"code": "JIAN", "name": "件", "category": uom_category["id"]})
        location = self.post("location", {"code": "RM01", "name": "原料仓"})
        category = self.post("product-category", {"code": "RM", "name": "原材料"})
        parent = self.post("material", {
            "code": "FG-001", "name": "成品", "category": category["id"], "uom": uom["id"],
            "default_location": location["id"], "tax_code": "1001",
        })
        component = self.post("material", {
            "code": "RM-001", "name": "组件", "category": category["id"], "uom": uom["id"],
            "default_location": location["id"], "tax_code": "1002",
        }) if with_component else None
        return uom, parent, component

    def test_bom_keeps_parent_component_quantity_and_source_relationship(self):
        uom, parent, component = self.material_context()
        bom = self.post("bom", {
            "code": "BOM-FG-001", "parent_material": parent["id"], "version": "A",
            "effective_date": "2026-08-20", "source_object": "bom_mstr",
        })
        line = self.post("bom-line", {
            "bom": bom["id"], "line_number": 10, "component": component["id"],
            "uom": uom["id"], "quantity": "2.5", "scrap_rate": "1.5",
            "operation": 20, "source_object": "ps_mstr",
        })
        self.assertEqual(line["component"], component["id"])
        self.assertEqual(line["quantity"], "2.500000")
        self.assertEqual(line["source_object"], "ps_mstr")
        payload = {"bom": bom["id"], "line_number": 20, "component": component["id"],
                   "uom": uom["id"], "quantity": "0.000001"}
        boundary = self.post("bom-line", payload)
        self.assertEqual(boundary["quantity"], "0.000001")
        for changes, field, message in (
            ({"quantity": "0"}, "quantity", "0.000001"),
            ({"component": parent["id"]}, "component", "BOM 组件不能与父物料相同"),
        ):
            with self.subTest(changes=changes):
                response = self.client.post("/api/bom-line/", {**payload, "line_number": 30, **changes}, format="json")
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn(message, str(response.data[field]))
        from backend.models import BomLine
        self.assertEqual(BomLine.objects.filter(bom_id=bom["id"]).count(), 2)

    def test_routing_keeps_ordered_operations_and_source_relationship(self):
        uom, parent, _ = self.material_context(with_component=False)
        routing = self.post("routing", {
            "code": "FG-001", "material": parent["id"], "version": "A",
            "source_object": "route_mstr",
        })
        operation = self.post("routing-operation", {
            "routing": routing["id"], "sequence": 20, "name": "组装",
            "work_center": "ASSY-01", "uom": uom["id"], "run_time": "1.25",
            "production_rate": "48", "yield_rate": "99.5", "is_default": True,
            "source_object": "ro_det",
        })
        self.assertEqual(operation["sequence"], 20)
        self.assertEqual(operation["work_center"], "ASSY-01")
        self.assertEqual(operation["source_object"], "ro_det")
        payload = {"routing": routing["id"], "sequence": 10, "name": "准备", "work_center": "PREP",
                   "uom": uom["id"], "yield_rate": "100"}
        boundary = self.post("routing-operation", payload)
        self.assertEqual(boundary["yield_rate"], "100.0000")
        ordered = self.client.get("/api/routing-operation/")
        self.assertEqual(ordered.status_code, 200, ordered.data)
        self.assertEqual([row["sequence"] for row in ordered.data], [10, 20])
        for changes, message in (({"sequence": 30, "yield_rate": "100.0001"}, "良率不能超过 100%"),
                                 ({"sequence": 30, "yield_rate": "-1"}, "0"),
                                 ({}, "唯一")):
            with self.subTest(changes=changes):
                response = self.client.post("/api/routing-operation/", {**payload, **changes}, format="json")
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn(message, str(response.data))
        from backend.models import RoutingOperation
        self.assertEqual(RoutingOperation.objects.filter(routing_id=routing["id"]).count(), 2)
