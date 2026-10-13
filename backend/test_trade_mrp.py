from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import override_settings
from rest_framework.test import APITestCase

from backend.test_support import CoreFlowSupport
from backend.models import Material, Location, SalesOrder, SalesOrderLine, StockBalance, PurchaseOrder, PurchaseOrderLine, PurchaseRequisition, PurchaseRequisitionLine
from backend.domain.trade_mrp import TradeMrpRun, TradeMrpSiteParameter, calculate_trade_mrp, confirm_trade_mrp, preview_trade_mrp_generation


@override_settings(ERP_TRADE_MRP_GENERATION_ENABLED=True)
class TradeMrpTests(CoreFlowSupport, APITestCase):
    def setUp(self):
        super().setUp()
        self.ctx = self.base_context()
        self.material = Material.objects.get(pk=self.ctx['material']['id'])
        self.material.quality_control = 'exempt'
        self.material.save(update_fields=['quality_control'])
        self.location = Location.objects.get(pk=self.ctx['location']['id'])
        self.location.source_site = '1000'
        self.location.save()

    def order(self, number, quantity, due='2026-10-10', **values):
        head = SalesOrder.objects.create(number=number, customer_id=self.ctx['customer']['id'],
            currency_id=self.ctx['currency']['id'], status=values.pop('status', 'approved'),
            site=values.pop('site', '1000'), promised_date='2026-10-01', customer_po=number,
            delivery_address='test', consignment=values.pop('consignment', False))
        row = SalesOrderLine.objects.create(order=head, line_number=10, material=self.material,
            uom=self.material.uom, quantity=Decimal(quantity), promised_date=due)
        if values:
            SalesOrderLine.objects.filter(pk=row.pk).update(**values)
        return row

    def stock(self, qty, **values):
        return StockBalance.objects.create(material=self.material, location=self.location,
            uom=self.material.uom, quantity=qty, **values)

    def req(self, qty, status='approved', **values):
        head = PurchaseRequisition.objects.create(status=status, site=values.pop('site', '1000'),
            requisition_type=values.pop('requisition_type', 'P'), source_profile=values.pop('source_profile', ''))
        return PurchaseRequisitionLine.objects.create(requisition=head, line_number=10,
            material=self.material, uom=self.material.uom, mrp_demand_qty=qty, requested_qty=qty, **values)

    def po(self, qty, status='approved', **values):
        head = PurchaseOrder.objects.create(supplier_id=self.ctx['customer']['id'],
            currency_id=self.ctx['currency']['id'], promised_date='2026-10-10', tax_rate=0,
            status=status, site=values.pop('site', '1000'), purchase_type=values.pop('purchase_type', 'production'))
        return PurchaseOrderLine.objects.create(order=head, line_number=10, material=self.material,
            uom=self.material.uom, quantity=qty, unit_price=0, promised_date='2026-10-10', **values)

    def result(self, **kwargs):
        return calculate_trade_mrp(**kwargs).results.get()

    def test_shared_stock_global_demand_and_source_filter(self):
        first = self.order('SO-1', '10')
        self.order('SO-2', '20', due='2026-10-20')
        self.stock(5)
        row = self.result(filters={'order': 'SO-1'})
        self.assertEqual((row.demand_qty, row.available_qty, row.suggested_qty), (30, 5, 25))
        self.assertEqual(len(row.source_snapshot), 1)
        self.assertEqual(row.source_snapshot[0]['sales_order_line_id'], first.pk)
        self.assertEqual(Decimal(row.source_snapshot[0]['supplement_qty']), 15)
        without = self.result(filters={'order': 'SO-1', 'last_pr': False})
        self.assertEqual(without.suggested_qty, 10)
        full = self.result()
        self.assertEqual(sum(Decimal(s['suggested_qty']) for s in full.source_snapshot), 25)
        self.assertEqual([s['analysis_sequence'] for s in full.source_snapshot], [1, 2])

    @override_settings(ERP_TRADE_MRP_GENERATION_ENABLED=False)
    def test_local_ledger_opt_in_identity_and_external_scope(self):
        from pathlib import Path
        from django.db import connection
        from backend.domain.inventory_reports import InventoryReportBatch
        from backend.trade_mrp_readiness import generation_readiness
        self.order('LOCAL-TEST', '10')
        batch = InventoryReportBatch.objects.create(source='local', active=True, manifest={
            'trade_mrp_local_test': {'enabled': True, 'site': '1000', 'version': 'scope-1',
                'database_path': str(Path(connection.settings_dict['NAME']).resolve()),
                'blocked_materials': {}, 'excluded_materials': [{'source_code': 'UNIT-X'}]}})
        self.assertTrue(generation_readiness()['enabled'])
        self.assertFalse(generation_readiness('2000')['enabled'])
        run = calculate_trade_mrp()
        batch.manifest['trade_mrp_local_test']['blocked_materials'] = {self.material.code: ['生产分配']}
        batch.manifest['trade_mrp_local_test']['version'] = 'scope-2'
        batch.save()
        with self.assertRaises(ValidationError):
            confirm_trade_mrp(run.pk)
        blocked = calculate_trade_mrp()
        self.assertIn('生产分配', str(blocked.results.get().calculation_snapshot['issues']))
        with self.assertRaises(ValidationError):
            confirm_trade_mrp(blocked.pk)
        batch.manifest['trade_mrp_local_test']['database_path'] = 'wrong-ledger.sqlite3'
        batch.save()
        self.assertFalse(generation_readiness()['enabled'])

    def test_range_filters_preserve_global_pool_and_freeze_descriptions(self):
        first = self.order('RANGE-01', '10')
        self.order('RANGE-02', '20')
        self.stock(5)
        SalesOrder.objects.filter(pk=first.order_id).update(order_date='2026-09-29', notes='来源订单备注')
        Material.objects.filter(pk=self.material.pk).update(english_name='Trade material', specification='10 x 20', planner='P01', buyer='B01')
        filters = {'order_from': 'RANGE-01', 'order_to': 'RANGE-01', 'line_from': 10, 'line_to': 10,
            'order_date_from': '2026-09-29', 'order_date_to': '2026-09-29',
            'material_from': self.material.code, 'material_to': self.material.code,
            'category_from': self.material.category.code, 'category_to': self.material.category.code,
            'planner': 'P01', 'buyer': 'B01'}
        row = self.result(filters=filters)
        self.assertEqual((row.demand_qty, row.shortage_qty), (30, 25))
        self.assertEqual([s['sales_order_line_id'] for s in row.source_snapshot], [first.pk])
        self.assertEqual(row.source_snapshot[0]['order_notes'], '来源订单备注')
        self.assertEqual(row.calculation_snapshot['material_info']['english_name'], 'Trade material')
        Material.objects.filter(pk=self.material.pk).update(english_name='Changed')
        row.refresh_from_db()
        self.assertEqual(row.calculation_snapshot['material_info']['english_name'], 'Trade material')
        self.assertFalse(calculate_trade_mrp(filters={**filters, 'buyer': 'B02'}).results.exists())
        for key, start, end in [('order', 'Z', 'A'), ('line', 20, 10),
                                ('order_date', '2026-10-01', '2026-09-29'),
                                ('material', 'Z', 'A'), ('category', 'Z', 'A')]:
            with self.subTest(key=key), self.assertRaises(ValidationError):
                calculate_trade_mrp(filters={f'{key}_from': start, f'{key}_to': end})

    def test_range_api_validates_and_applies_source_boundaries(self):
        first = self.order('API-RANGE-01', '10')
        self.order('API-RANGE-02', '20')
        response = self.client.post('/api/trade-mrp/preview/', {'order_from': 'API-RANGE-01',
            'order_to': 'API-RANGE-01', 'line_from': 10, 'line_to': 10}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        row = response.data['results'][0]
        self.assertEqual(Decimal(row['demand_qty']), 30)
        self.assertEqual([s['sales_order_line_id'] for s in row['source_snapshot']], [first.pk])
        for values in [{'line_from': -1}, {'line_from': 'bad'}, {'order_date_from': 'not-a-date'},
                       {'line_from': 20, 'line_to': 10}]:
            with self.subTest(values=values):
                self.assertEqual(self.client.post('/api/trade-mrp/preview/', values, format='json').status_code, 400)

    def test_descriptive_dictionary_uses_source_baseline_and_freezes_names(self):
        from backend.domain.inventory_reports import InventoryReportBatch, InventoryReportLookup
        self.order('DICT-01', '10')
        Material.objects.filter(pk=self.material.pk).update(product_group='G1', part_type='T1')
        baseline = InventoryReportBatch.objects.create(source='coerp_dgyzx1', active=False)
        InventoryReportLookup.objects.create(batch=baseline, kind='group', code='G1', name='产品组一', source_order=1)
        InventoryReportLookup.objects.create(batch=baseline, kind='part_type', code='T1', name='零件类型一', source_order=1)
        active = InventoryReportBatch.objects.create(source='local', active=True, manifest={'baseline_batch_id': baseline.pk})
        row = self.result()
        self.assertEqual(row.calculation_snapshot['material_info']['product_group_name'], '产品组一')
        self.assertEqual(row.calculation_snapshot['material_info']['part_type_name'], '零件类型一')
        InventoryReportLookup.objects.filter(batch=baseline, kind='group').update(name='新名称')
        row.refresh_from_db()
        self.assertEqual(row.calculation_snapshot['material_info']['product_group_name'], '产品组一')
        active.source = 'other-ledger'
        active.save()
        self.assertEqual(self.result().calculation_snapshot['material_info']['product_group_name'], '')

    def test_ppt_frozen_example_and_real_two_order_arithmetic(self):
        self.order('MYSO26070483', '19700')
        self.order('OTHER-SOURCE', '35000')
        self.stock(18750)
        self.po(700)
        row = self.result(filters={'order': 'MYSO26070483'})
        self.assertEqual((row.demand_qty, row.shortage_qty, row.suggested_qty), (54700, 35250, 35250))
        self.assertEqual(Decimal(row.source_snapshot[0]['supplement_qty']), 15550)

    def test_dgyzx1_bhm_000142_frozen_two_order_sample(self):
        # Captured by tools.probe_trade_mrp_sample on 2026-10-06, independent of live DB.
        self.order('MYSO26080506', '100000')
        self.order('MYSO26090568', '80000')
        self.po(100000)
        self.po(80000)
        row = self.result()
        self.assertEqual((row.demand_qty, row.on_order_qty, row.shortage_qty), (180000, 180000, 0))
        self.assertEqual(len(row.source_snapshot), 2)

    def test_approved_supply_pending_coverage_and_site_isolation(self):
        self.order('SO-A', '100')
        self.order('SO-DRAFT', '900', status='draft')
        self.order('SO-OTHER', '800', site='2000')
        self.stock(10)
        self.po(20)
        self.po(500, status='draft')
        self.po(500, purchase_type='outsource')
        self.po(500, site='2000')
        self.req(15, converted_qty=5)
        self.req(5, status='draft', source_profile='trade_mrp', source_kind='trade_mrp')
        self.req(500, status='draft')  # Unapproved manual/imported drafts are not committed MRP coverage.
        self.req(500, status='rejected')
        self.req(500, requisition_type='S')
        row = self.result()
        self.assertEqual((row.demand_qty, row.on_order_qty, row.approved_requisition_qty, row.pending_requisition_qty, row.suggested_qty), (100, 20, 10, 5, 55))

    def test_zero_shortage_is_retained_and_line_date_is_used(self):
        self.order('SO-A', '10', due='2026-11-15')
        self.stock(30)
        row = self.result(filters={'date_from': '2026-11-01'})
        self.assertEqual(row.shortage_qty, 0)
        self.assertEqual(str(row.needed_date), '2026-11-15')
        self.assertEqual(len(row.source_snapshot), 1)

    def test_formal_and_spare_positive_balances_differ_from_global_algebra(self):
        self.order('SO-A', '10', spare_quantity=5, delivered_quantity=12, delivered_spare_quantity=1)
        row = self.result()
        self.assertEqual(Decimal(row.source_snapshot[0]['quantity']), 4)
        self.assertEqual(row.demand_qty, 2)

    def test_source_packaging_carry_and_minimum_not_multiple(self):
        self.order('SO-A', '3')
        self.order('SO-B', '3', due='2026-10-11')
        Material.objects.filter(pk=self.material.pk).update(min_pack_qty=10)
        row = self.result()
        self.assertEqual(row.suggested_qty, 10)
        self.assertEqual([Decimal(s['suggested_qty']) for s in row.source_snapshot], [10, 0])
        Material.objects.filter(pk=self.material.pk).update(min_purchase_qty=15)
        self.assertEqual(self.result().suggested_qty, 15)
        self.assertEqual(self.result(filters={'last_pr': False}).suggested_qty, 6)

    def test_generated_draft_prevents_repeat_and_stales_other_run(self):
        self.order('SO-A', '10')
        first, second = calculate_trade_mrp(), calculate_trade_mrp()
        req = confirm_trade_mrp(first.pk, actor='tester')
        self.assertEqual((req.status, req.requisition_type), ('draft', 'P'))
        self.assertEqual(req.lines.get().sources.get().quantity, 10)
        self.assertEqual(confirm_trade_mrp(first.pk).pk, req.pk)
        with self.assertRaisesMessage(ValidationError, '重新计算'):
            confirm_trade_mrp(second.pk)
        row = self.result()
        self.assertEqual((row.pending_requisition_qty, row.shortage_qty), (10, 0))
        req.status = 'rejected'; req.save()
        self.assertEqual(self.result().shortage_qty, 10)

    def test_adjustment_and_partial_source_selection_reconcile(self):
        first = self.order('SO-A', '10')
        self.order('SO-B', '20', due='2026-10-11')
        run = calculate_trade_mrp()
        row = run.results.get()
        req = confirm_trade_mrp(run.pk, selected_sources=[first.pk], quantities={str(row.pk): '7.125'}, adjustment_reason='partial purchase')
        line = req.lines.get()
        self.assertEqual(line.requested_qty, Decimal('7.125'))
        self.assertEqual(line.sources.count(), 1)
        self.assertEqual(line.sources.get().source_number, 'SO-A')
        self.assertEqual(line.sources.get().source_marker, '10')
        self.assertEqual(line.sources.get().source_sequence, 1)
        self.assertEqual(line.sources.get().quantity, Decimal('7.125'))
        self.assertEqual(line.calculation_snapshot['adjustment_reason'], 'partial purchase')

    def test_invalid_quantity_and_missing_reason_rollback(self):
        self.order('SO-A', '10')
        run = calculate_trade_mrp(); row = run.results.get()
        for qty in ['abc', '-1', 'NaN', 'Infinity', '100000000000', '1.000000001', '']:
            with self.subTest(qty=qty), self.assertRaises(ValidationError):
                confirm_trade_mrp(run.pk, quantities={str(row.pk): qty}, adjustment_reason='invalid')
        with self.assertRaisesMessage(ValidationError, '原因'):
            confirm_trade_mrp(run.pk, quantities={str(row.pk): '11'})
        self.assertFalse(PurchaseRequisition.objects.exists())

    def test_non_one_to_one_demand_blocks_even_outside_filter(self):
        self.order('SO-A', '10')
        self.order('SO-B', '20', uom_rate_m=2)
        run = calculate_trade_mrp(filters={'order': 'SO-A'})
        self.assertTrue(run.results.get().calculation_snapshot['issues'])
        with self.assertRaisesMessage(ValidationError, '1:1'):
            confirm_trade_mrp(run.pk)
        self.assertFalse(PurchaseRequisition.objects.exists())

    def test_non_one_to_one_purchase_and_changed_rate_block(self):
        self.order('SO-A', '100')
        purchase = self.po(10)
        run = calculate_trade_mrp()
        PurchaseOrderLine.objects.filter(pk=purchase.pk).update(uom_rate_d=2)
        with self.assertRaisesMessage(ValidationError, '重新计算'):
            confirm_trade_mrp(run.pk)
        run = calculate_trade_mrp()
        with self.assertRaisesMessage(ValidationError, '1:1'):
            confirm_trade_mrp(run.pk)

    def test_excluded_and_unassigned_stock_and_negative_available(self):
        self.order('SO-A', '10')
        balance = self.stock(-2)
        self.assertEqual(self.result().shortage_qty, 12)
        self.location.source_site = '2000'; self.location.save()
        self.assertEqual(self.result().available_qty, 0)
        self.location.source_site = ''; self.location.save()
        self.assertTrue(self.result().calculation_snapshot['issues'])
        self.location.source_site = '1000'; self.location.usable = False; self.location.save()
        StockBalance.objects.filter(pk=balance.pk).update(quantity=20)
        row = self.result()
        self.assertEqual((row.available_qty, Decimal(row.calculation_snapshot['unavailable_qty'])), (0, 20))

    def test_consignment_filter(self):
        from backend.models import Partner
        Partner.objects.filter(pk=self.ctx['customer']['id']).update(consignment=True)
        self.order('SO-EXCLUDE', '100')
        self.order('SO-INCLUDE', '10', consignment=True)
        self.assertEqual(self.result().demand_qty, 10)

    def test_site_parameter_precedence_null_fallback_and_staleness(self):
        self.order('SO-A', '6')
        Material.objects.filter(pk=self.material.pk).update(min_pack_qty=10, safety_stock_qty=100)
        parameter = TradeMrpSiteParameter.objects.create(site='1000', material=self.material,
            safety_stock_qty=0, min_purchase_qty=15, min_pack_qty=None)
        TradeMrpSiteParameter.objects.create(site='2000', material=self.material, safety_stock_qty=900)
        row = self.result()
        self.assertEqual((row.safety_stock_qty, row.shortage_qty, row.suggested_qty), (0, 6, 15))
        parameter.min_purchase_qty = 20; parameter.save()
        with self.assertRaisesMessage(ValidationError, '重新计算'):
            confirm_trade_mrp(row.run_id)

    def test_unapproved_conversion_blocks_duplicate_requisition(self):
        self.order('SO-A', '100')
        source = self.req(100)
        purchase = self.po(30, status='draft', source_requisition_line=source)
        run = calculate_trade_mrp()
        with self.assertRaisesMessage(ValidationError, '尚未审核'):
            confirm_trade_mrp(run.pk)
        PurchaseOrder.objects.filter(pk=purchase.order_id).update(status='approved')
        self.assertEqual(self.result().shortage_qty, 0)

    def test_api_preview_confirm_invalid_input_and_old_route(self):
        row = self.order('SO-A', '10')
        for data in [{'mode': 'demand'}, {'date_from': 'bad'}, {'date_from': '2026-11-01', 'date_to': '2026-10-01'}]:
            response = self.client.post('/api/trade-mrp/preview/', data, format='json')
            self.assertEqual(response.status_code, 400, response.data)
        response = self.client.post('/api/trade-mrp/preview/', {'site': '1000', 'date_from': None}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['results'][0]['uom_name'], self.material.uom.name)
        url = f"/api/trade-mrp/{response.data['id']}/confirm/"
        invalid = self.client.post(url, {'quantities': {'unknown': '5'}}, format='json')
        self.assertEqual(invalid.status_code, 400)
        generated = self.client.post(url, {}, format='json')
        self.assertEqual(generated.status_code, 201, generated.data)
        repeated = self.client.post(url, {}, format='json')
        self.assertEqual(repeated.status_code, 201)
        self.assertEqual(repeated.data['id'], generated.data['id'])
        self.assertEqual(self.client.post(f'/api/sales-order/{row.order_id}/generate-requisition/', {}, format='json').status_code, 400)
        self.assertEqual(TradeMrpRun.objects.filter(status='confirmed').count(), 1)

    def test_source_adjustments_do_not_merge_same_material_or_change_unselected_rows(self):
        first = self.order('SO-A', '10')
        second = self.order('SO-B', '20', due='2026-10-20')
        run = calculate_trade_mrp()
        values = dict(selected_sources=[first.pk, second.pk],
            source_quantities={str(first.pk): '7.125', str(second.pk): '23'}, adjustment_reason='按来源分批购买')
        plan = preview_trade_mrp_generation(run.pk, **values)
        self.assertFalse(PurchaseRequisition.objects.exists())
        self.assertEqual([x['quantity'] for x in plan['lines']], ['7.125', '23'])
        req = confirm_trade_mrp(run.pk, **values)
        self.assertEqual(req.aggregation_mode, 'none')
        self.assertEqual(list(req.lines.values_list('source_sales_order_line_id', flat=True)), [first.pk, second.pk])
        self.assertEqual(list(req.lines.values_list('requested_qty', flat=True)), [Decimal('7.125'), Decimal('23')])
        self.assertEqual(confirm_trade_mrp(run.pk, **values).pk, req.pk)
        with self.assertRaisesMessage(ValidationError, '其他数量'):
            confirm_trade_mrp(run.pk, source_quantities={str(first.pk): '8', str(second.pk): '23'},
                selected_sources=[first.pk, second.pk], adjustment_reason='changed')
        for line in req.lines.all():
            self.assertEqual(line.requested_qty, line.sources.get().quantity)

    def test_summary_adjustment_requires_explicit_source_and_rejects_unselected_quantity(self):
        first = self.order('SO-A', '10')
        second = self.order('SO-B', '20')
        run = calculate_trade_mrp()
        with self.assertRaisesMessage(ValidationError, '逐行调量'):
            confirm_trade_mrp(run.pk, quantities={str(run.results.get().pk): '30'})
        with self.assertRaisesMessage(ValidationError, '已选'):
            confirm_trade_mrp(run.pk, selected_sources=[first.pk], source_quantities={str(second.pk): '10'})

    def test_dgyzx1_same_material_two_orders_retain_separate_requisition_lines(self):
        # Frozen shape: MYPR26090569 lines 10/60, from live read-only evidence.
        first = self.order('MYSO26090739', '32', due='2026-10-07')
        second = self.order('MYSO26090740', '40', due='2026-10-08')
        SalesOrderLine.objects.filter(pk=first.pk).update(line_number=2)
        SalesOrderLine.objects.filter(pk=second.pk).update(line_number=3)
        from datetime import date
        with patch('backend.domain.trade_mrp.timezone.localdate', return_value=date(2026, 10, 6)):
            run = calculate_trade_mrp()
            req = confirm_trade_mrp(run.pk)
        self.assertEqual(req.lines.count(), 2)
        lines = list(req.lines.all())
        self.assertEqual([line.requested_qty for line in lines], [32, 40])
        self.assertEqual([str(line.needed_date) for line in lines], ['2026-10-07', '2026-10-08'])
        self.assertEqual([line.sources.get().source_number for line in lines], ['MYSO26090739', 'MYSO26090740'])
        self.assertEqual([line.sources.get().source_marker for line in lines], ['2', '3'])
        self.assertEqual([line.sources.get().sequence for line in lines], [10, 10])

    def test_edit_live_allocation_preserves_original_snapshot_and_delete_releases_coverage(self):
        self.order('SO-A', '10')
        run = calculate_trade_mrp()
        req = confirm_trade_mrp(run.pk)
        line = req.lines.get()
        original = line.sources.get().snapshot
        response = self.client.patch(f'/api/purchase-requisition/{req.pk}/',
            {'version': req.version, 'lines': [{'id': line.pk, 'requested_qty': '4.125'}]}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        line.refresh_from_db()
        self.assertEqual(line.sources.get().quantity, Decimal('4.125'))
        self.assertEqual(line.sources.get().snapshot, original)
        self.assertEqual(self.result().shortage_qty, Decimal('5.875'))
        self.assertEqual(self.client.delete(f'/api/purchase-requisition/{req.pk}/').status_code, 204)
        self.assertEqual(self.result().shortage_qty, 10)
        run.refresh_from_db()
        self.assertEqual(run.status, 'confirmed')
        self.assertEqual(run.confirmation_snapshot['requisition_number'], req.number)
        with self.assertRaisesMessage(ValidationError, '已删除'):
            confirm_trade_mrp(run.pk)

    def test_quality_and_nontrade_materials_are_blocked_instead_of_only_warned(self):
        self.order('SO-A', '10')
        for fields, message in [({'inspection_required': True}, '需检'),
                ({'inspection_required': False, 'no_stock_movement': True}, '非普通'),
                ({'no_stock_movement': False, 'supply_method': 'manufacture'}, '非普通'),
                ({'supply_method': 'purchase', 'active': False}, '停用')]:
            Material.objects.filter(pk=self.material.pk).update(**fields)
            run = calculate_trade_mrp()
            with self.assertRaisesMessage(ValidationError, message):
                confirm_trade_mrp(run.pk)
        self.assertFalse(PurchaseRequisition.objects.exists())

    def test_quality_configuration_conflict_is_not_treated_as_exemption(self):
        self.order('SO-A', '10')
        Material.objects.filter(pk=self.material.pk).update(quality_control='required', inspection_required=False)
        run = calculate_trade_mrp()
        with self.assertRaisesMessage(ValidationError, '不一致'):
            confirm_trade_mrp(run.pk)

    def test_source_dates_clamp_without_erasing_original_due_or_quality_lead(self):
        from datetime import date
        self.order('SO-A', '10', due='2026-09-20')
        Material.objects.filter(pk=self.material.pk).update(inspection_required=True, quality_lead_days=3)
        with patch('backend.domain.trade_mrp.timezone.localdate', return_value=date(2026, 10, 6)):
            source = self.result().source_snapshot[0]
        self.assertEqual((source['promised_date'], source['arrival_before_clamp'], source['arrival_date']),
            ('2026-09-20', '2026-09-17', '2026-10-06'))
        self.assertTrue(source['overdue'])

    def test_history_cancel_preview_header_and_unauthenticated_access(self):
        self.order('SO-A', '10')
        run = calculate_trade_mrp()
        url = f'/api/trade-mrp/{run.pk}/generation-preview/'
        response = self.client.post(url, {'header': {'requester': 'missing employee'}}, format='json')
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, {'header': {'requester': self.user.username, 'request_date': '2026-10-06'}}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(PurchaseRequisition.objects.exists())
        self.assertEqual(self.client.get('/api/trade-mrp/?site=1000').data['results'][0]['id'], run.pk)
        self.assertEqual(self.client.post(f'/api/trade-mrp/{run.pk}/cancel/', {}, format='json').status_code, 200)
        with self.assertRaisesMessage(ValidationError, '已取消'):
            confirm_trade_mrp(run.pk)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post(url, {}, format='json').status_code, 401)

    def test_customer_mapping_selection_does_not_shrink_global_material_demand(self):
        from backend.models import CustomerMaterial
        first = self.order('SO-A', '10')
        second = self.order('SO-B', '20')
        mapping_a = CustomerMaterial.objects.create(customer_id=first.order.customer_id, material=self.material,
            customer_code='CUSTOMER-A', terminal_customer_code='TERMINAL-ONE')
        mapping_b = CustomerMaterial.objects.create(customer_id=first.order.customer_id, material=self.material,
            customer_code='CUSTOMER-B', terminal_customer_code='TERMINAL-ONE')
        SalesOrderLine.objects.filter(pk=first.pk).update(customer_material=mapping_a)
        SalesOrderLine.objects.filter(pk=second.pk).update(customer_material=mapping_b)
        matches = self.client.get('/api/trade-mrp/customer-materials/?q=TERMINAL-ONE')
        self.assertEqual({r['id'] for r in matches.data}, {mapping_a.pk, mapping_b.pk})
        response = self.client.post('/api/trade-mrp/preview/', {'customer_material_id': mapping_a.pk}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        row = response.data['results'][0]
        self.assertEqual(Decimal(row['demand_qty']), 30)
        self.assertEqual([s['sales_order_line_id'] for s in row['source_snapshot']], [first.pk])

    def test_source_failure_rolls_back_document_and_batch_confirmation(self):
        self.order('SO-A', '10')
        run = calculate_trade_mrp()
        with patch('backend.domain.trade_mrp.PurchaseRequisitionSource.objects.create', side_effect=ValidationError('source insert failed')):
            with self.assertRaisesMessage(ValidationError, 'source insert failed'):
                confirm_trade_mrp(run.pk)
        self.assertFalse(PurchaseRequisition.objects.exists())
        run.refresh_from_db()
        self.assertEqual(run.status, 'preview')
        self.assertFalse(run.confirmation_snapshot)

    def test_generation_header_date_numbering_and_semantic_retry(self):
        source = self.order('SO-A', '10')
        run = calculate_trade_mrp()
        body = {'header': {'requester': self.user.username, 'request_date': '2026-10-06', 'notes': 'MRP header'},
            'selected_sources': [source.pk], 'source_quantities': {str(source.pk): '10'}}
        url = f'/api/trade-mrp/{run.pk}/confirm/'
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        req = PurchaseRequisition.objects.get(pk=response.data['id'])
        self.assertTrue(req.number.startswith('MYPR2610'))
        self.assertEqual(str(req.request_date), '2026-10-06')
        self.assertEqual(req.notes, 'MRP header')
        body['source_quantities'][str(source.pk)] = '10.00000000'
        repeated = self.client.post(url, body, format='json')
        self.assertEqual(repeated.status_code, 201, repeated.data)
        self.assertEqual(repeated.data['id'], req.pk)

    @override_settings(ERP_TRADE_MRP_GENERATION_ENABLED=False)
    def test_generation_switch_does_not_disable_readonly_analysis(self):
        self.order('SO-A', '10')
        run = calculate_trade_mrp()
        self.assertEqual(len(preview_trade_mrp_generation(run.pk)['lines']), 1)
        with self.assertRaisesMessage(ValidationError, '尚未启用'):
            confirm_trade_mrp(run.pk)
