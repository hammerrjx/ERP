"""Engineering active flag uses the existing material approval lifecycle."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from backend.test_support import CoreFlowSupport
from backend.models import Material, StockBalance, StockTransaction


class MaterialActiveTests(CoreFlowSupport, APITestCase):
    def test_active_round_trip_controls_new_business_without_changing_stock(self):
        ctx = self.base_context()
        material = Material.objects.get(pk=ctx['material']['id'])
        url = f'/api/material/{material.pk}/'
        self.assertTrue(material.active)
        self.post('stock-balance', {'material': material.pk, 'location': ctx['location']['id'],
                                  'uom': ctx['uom']['id'], 'quantity': '150000'})
        stock = list(StockBalance.objects.values())
        transactions = StockTransaction.objects.count()

        def selectable(expected):
            for resource in ('purchase-requisition', 'purchase-order'):
                result = self.client.get(f'/api/{resource}/lookups/', {'kind': 'material', 'q': material.code})
                self.assertEqual(result.status_code, 200, result.data)
                self.assertEqual(any(r['id'] == material.pk for r in result.data), expected)

        selectable(True)
        self.assertEqual(self.client.patch(url, {'active': False}, format='json').status_code, 400)
        for active in (False, True):
            self.assertEqual(self.client.post(url + 'unapprove/').status_code, 200)
            result = self.client.patch(url, {'active': active}, format='json')
            self.assertEqual(result.status_code, 200, result.data)
            self.assertEqual(self.client.get(url).data['active'], active)
            selectable(False)
            self.approve('material', material.pk)
            selectable(active)
            req = self.client.post('/api/purchase-requisition/', {'lines': [
                {'material': material.pk, 'requested_qty': '1'}]}, format='json')
            self.assertEqual(req.status_code, 201 if active else 400, req.data)
        self.assertEqual(list(StockBalance.objects.values()), stock)
        self.assertEqual(StockTransaction.objects.count(), transactions)
        material.refresh_from_db()
        self.assertEqual(material.code, ctx['material']['code'])
        self.client.force_authenticate(get_user_model().objects.create_user('material-reader'))
        self.assertEqual(self.client.patch(url, {'active': False}, format='json').status_code, 403)
        self.assertEqual(self.client.post(url + 'unapprove/').status_code, 403)
