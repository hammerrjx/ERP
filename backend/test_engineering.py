from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from backend.test_support import SourceDatabaseIsolatedMixin


class EngineeringApiTests(SourceDatabaseIsolatedMixin, APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("engineer", password="pass")
        self.client.force_authenticate(self.user)

    def post(self, resource, payload):
        response = self.client.post(f"/api/{resource}/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def material_context(self):
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
        })
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

    def test_routing_keeps_ordered_operations_and_source_relationship(self):
        uom, parent, _ = self.material_context()
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
