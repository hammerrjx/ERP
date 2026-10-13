from decimal import Decimal
from rest_framework.test import APITestCase
from backend.test_support import CoreFlowSupport
from backend.models import SupplierQuote, Partner, Material


class SupplierQuotePagingTests(CoreFlowSupport, APITestCase):
    def test_paging_search_and_legacy_list_keep_all_relations(self):
        context = self.base_context()
        supplier = Partner.objects.create(code='PAGING-SUP', name='分页供应商', short_name='分页供',
                                          kind='supplier', currency_id=context['currency']['id'], status='approved')
        material = Material.objects.get(pk=context['material']['id'])
        for index in range(53):
            SupplierQuote.objects.create(number=f'PAGING-{index:04}', supplier=supplier, material=material,
                                         currency_id=context['currency']['id'], purchase_uom_id=context['uom']['id'],
                                         effective_date='2026-09-01', material_unit_price=Decimal('1'))
        first = self.client.get('/api/supplier-quote/?page=1&page_size=50')
        second = self.client.get('/api/supplier-quote/?page=2&page_size=50')
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.data['count'], 53)
        self.assertEqual(len(first.data['results']), 50)
        self.assertEqual(len(second.data['results']), 3)
        self.assertFalse({r['id'] for r in first.data['results']} & {r['id'] for r in second.data['results']})
        self.assertEqual(first.data['results'][0]['material_code'], material.code)
        found = self.client.get('/api/supplier-quote/?page=1&q=PAGING-0007')
        self.assertEqual(found.data['count'], 1)
        self.assertEqual(len(self.client.get('/api/supplier-quote/').data), 53)
        candidates = self.client.get(f'/api/material/candidates/?kind=suppliers&q=PAGING&selected={supplier.pk}')
        self.assertEqual(candidates.status_code, 200)
        self.assertEqual(candidates.data[0]['currency'], context['currency']['id'])
