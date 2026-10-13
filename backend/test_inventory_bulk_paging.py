from unittest.mock import patch

from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from backend.test_support import CoreFlowSupport
from backend.models import Location
from backend.domain.inventory_analysis import InventoryAnalysisSnapshot
from backend.domain.inventory_reports import InventoryReportBatch, InventoryReportRow


class InventoryBulkPagingTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        Location.objects.create(code='RAW1', name='仓库', source_site='1000', participate_mrp=True)
        self.snapshot = InventoryAnalysisSnapshot.objects.create(kind='localbulk', site='1000', payload={
            'rows': [{'tmp_part': f'P{i:03}', 'pt_desc1': '筛选名称', 'tmp_qty_oh': '0', 'tmp_sfty_stk': '1'} for i in range(205)],
            'details': []})
        self.batch = InventoryReportBatch.objects.create(source='local', active=True)
        InventoryReportRow.objects.bulk_create([InventoryReportRow(batch=self.batch, kind='inventory',
            site='1000', material_code=code, source_table='stock_balance', source_key=code,
            location_code='RAW1', payload={'quantity': str(i), 'uom_name': '件'})
            for i, code in enumerate([f'P{i:03}' for i in range(205)] + ['A001', 'P099A', 'Z001'])])

    def test_pages_match_full_live_calculation_including_new_materials(self):
        url = '/api/material-inventory-batch/'
        for direction in ('asc', 'desc'):
            for page in (1, 10, 11, 21, 22):
                params = {'site': '1000', 'source': 'local', 'page': page, 'page_size': 10, 'direction': direction}
                original = self.client.get(url, params)
                with patch('backend.master_data.inventory_analysis_views.snapshot_payload', side_effect=AssertionError('full capture read')):
                    with CaptureQueriesContext(connection) as queries:
                        paged = self.client.get(url, {**params, 'page_mode': '1'})
                self.assertEqual(paged.status_code, 200, paged.data)
                self.assertEqual(paged.data['count'], original.data['count'])
                self.assertEqual(paged.data['results'], original.data['results'])
                self.assertEqual(paged.data['totals_scope'], 'page')
                self.assertFalse(any('"backend_inventoryanalysissnapshot"."payload"' in q['sql'] for q in queries))
        for filters in ({'material_from': 'P099', 'material_to': 'P103'}, {'q': '筛选名称'}):
            original = self.client.get(url, filters).data
            paged = self.client.get(url, {**filters, 'page_mode': '1'}).data
            self.assertEqual(paged['results'], original['results'])
            self.assertEqual(paged['count'], original['count'])

    def test_capture_refresh_details_and_live_changes_do_not_return_stale_data(self):
        url = '/api/material-inventory-batch/'
        with patch('backend.master_data.inventory_analysis_views.snapshot_payload', side_effect=AssertionError('full capture read')):
            detail = self.client.get(url + 'details/', {'part': 'P001'}).data
            self.assertEqual(detail['total'], '1')
        row = InventoryReportRow.objects.get(material_code='P001')
        row.payload['quantity'] = '42'
        row.save()
        data = self.client.get(url, {'page_mode': '1', 'material_from': 'P001', 'material_to': 'P001'}).data
        self.assertEqual(data['results'][0]['tmp_qty_oh'], '42')
        self.snapshot.payload['rows'][1]['pt_desc1'] = '更新名称'
        self.snapshot.save(update_fields=['payload'])
        data = self.client.get(url, {'page_mode': '1', 'q': '更新名称'}).data
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['tmp_part'], 'P001')
        with self.assertNumQueries(0):
            self.assertEqual(self.client.get(url + 'choices/').data['periods'], [])
