from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from backend.test_support import SourceDatabaseIsolatedMixin


class InventoryApiTests(SourceDatabaseIsolatedMixin, APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("warehouse-admin", password="pass")
        self.client.force_authenticate(self.user)

    def test_location_references_warehouse_and_preserves_source_keys(self):
        warehouse = self.client.post("/api/warehouse/", {
            "code": "SITE01", "name": "制造一厂", "source_object": "si_mstr",
        }, format="json")
        self.assertEqual(warehouse.status_code, 201, warehouse.data)
        location = self.client.post("/api/location/", {
            "code": "RM01", "name": "原料仓", "warehouse": warehouse.data["id"],
            "source_site": "SITE01", "source_object": "loc_mstr",
        }, format="json")
        self.assertEqual(location.status_code, 201, location.data)
        self.assertEqual(location.data["warehouse"], warehouse.data["id"])
        self.assertEqual(location.data["source_site"], "SITE01")
