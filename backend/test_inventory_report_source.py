import gzip
import hashlib
import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, SimpleTestCase

from backend.domain.inventory import StockBalance, StockTransaction
from backend.domain.inventory_reports import InventoryReportBatch, InventoryReportRow
from backend.inventory_report_source import SourceReportMapper


def masters():
    return dict(pt_mstr=[dict(pt_part='P1', pt_desc1='测试物料', pt_spec='10mm', pt_prod_line='P', pt_keeper='E1', pt_um='PCS')],
                loc_mstr=[dict(loc_site='1000', loc_loc='A1', loc_type='ASM', loc_desc='半成品')],
                pl_mstr=[dict(pl_prod_line='P', pl_desc='产品')], um_mstr=[dict(um_um='PCS', um_desc='件')],
                usr_mstr=[dict(usr_user='E1', usr_name='仓管员')],
                gend_det=[dict(gend_gen='TR_TYPE', gend_option='120', gend_name='采购收货')],
                ptp3_det=[dict(ptp3_site='1000', ptp3_part='P1', **{f'ptp3_{c}_std{l}': '1.25' for c in ('mtl', 'lbr', 'bdn', 'sub') for l in ('tl', 'll')})],
                cp_mstr=[dict(cp_part='P1', cp_cust='C1', cp_cust_part='CP01'), dict(cp_part='P1', cp_cust='C2', cp_cust_part='CP02')],
                sc_mstr=[dict(sc_nbr='Q01', sc_part='P1', sc_cust='C1', sc_curr='CNY', sc_um_rate_m='10', sc_um_rate_d='1',
                              sc_start='2026-01-01', sc_expire='2026-12-31', sc_vat=True, sc_vat_rate='13', sc_pst=True, sc_price='113')],
                lots=[dict(site='1000', code='00001')])


def inventory():
    return dict(ld_site='1000', ld_loc='A1', ld_part='P1', ld_lot='00001', ld_qty_oh='2.00000001')


class SourceMappingTests(SimpleTestCase):
    def test_cost_quote_units_tax_multiple_customers_and_missing_values(self):
        source = masters()
        mapper = SourceReportMapper(source, '2026-09-16')
        row = mapper.map('ld_det', inventory())
        self.assertEqual(row['standard_cost'], '10.00')
        self.assertEqual(row['inventory_amount'], '20.00')
        self.assertEqual(row['sales_price'], '10.00000000')
        self.assertEqual(row['sales_amount'], '20.00')
        self.assertEqual(row['keeper_name'], '仓管员')
        self.assertEqual(row['customer_material_code'], 'C1: CP01; C2: CP02')
        source['sc_mstr'].append({**source['sc_mstr'][0], 'sc_cust': 'C2', 'sc_nbr': 'Q02'})
        self.assertIsNone(SourceReportMapper(source, '2026-09-16').map('ld_det', inventory())['sales_price'])
        source['ptp3_det'] = []
        self.assertIsNone(SourceReportMapper(source, '2026-09-16').map('ld_det', inventory())['inventory_amount'])

    def test_sign_batch_and_501_document_fields(self):
        mapper = SourceReportMapper(masters(), '2026-09-16')
        raw = dict(tr_trnbr=1, tr_type='120', tr_site='1000', tr_loc='A1', tr_part='P1', tr_qty_loc='-2.5',
                   tr_lotserial='00001', tr_lot='FLAG', tr_um_stk='PCS', tr_ref='DOC1', tr_nbr='ORDER1', tr_ref_line=10, tr_line=20)
        row = mapper.map('tr_hist', raw)
        self.assertEqual(row['receipt_quantity'], '0')
        self.assertEqual(row['issue_quantity'], '2.5')
        self.assertEqual(row['batch_number'], '00001')
        self.assertEqual(row['flag'], 'FLAG')
        raw['tr_type'] = '501'
        row = mapper.map('tr_hist', raw)
        self.assertEqual(row['document_number'], 'DOC1')
        self.assertEqual(row['display_document_number'], 'ORDER1')
        self.assertEqual(row['document_line'], '20')


class SourceImportTests(TestCase):
    def export(self, root):
        (root / 'masters.json').write_text(json.dumps(masters()), encoding='utf8')
        for table, rows in [('ld_det', [inventory()]), ('tr_hist', []), ('tr_hist_rec', [])]:
            with gzip.open(root / (table + '.jsonl.gz'), 'wt', encoding='utf8') as stream:
                for row in rows:
                    stream.write(json.dumps(row) + '\n')
        hashes = {}
        for path in root.iterdir():
            with path.open('rb') as stream:
                hashes[path.name] = hashlib.file_digest(stream, 'sha256').hexdigest()
        manifest = dict(source='coerp_dgyzx1', date_from='2026-01-01', date_to='2026-12-31', finished_at='2026-09-16',
                        counts={'ld_det': 1, 'tr_hist': 0, 'tr_hist_rec': 0}, sha256=hashes)
        (root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf8')

    def test_import_validation_activation_idempotence_and_ledger_isolation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.export(root)
            kwargs = dict(input=root, stdout=StringIO(), backup_dir=root / 'backups')
            call_command('import_inventory_reports', **kwargs)
            self.assertFalse(InventoryReportBatch.objects.exists())
            # Test DB is in memory; skip only the filesystem backup, not import behavior.
            from unittest.mock import patch
            with patch('backend.management.commands.import_inventory_reports.connection') as connection:
                connection.vendor = 'test'
                call_command('import_inventory_reports', apply=True, **kwargs)
                call_command('import_inventory_reports', apply=True, activate=True, **kwargs)
                call_command('import_inventory_reports', apply=True, activate=True, **kwargs)
            self.assertEqual(InventoryReportBatch.objects.filter(active=True).count(), 1)
            self.assertEqual(InventoryReportRow.objects.count(), 1)
            self.assertEqual(StockBalance.objects.count(), 0)
            self.assertEqual(StockTransaction.objects.count(), 0)
            (root / 'masters.json').write_text('{}', encoding='utf8')
            with self.assertRaises(CommandError):
                call_command('import_inventory_reports', apply=True, **kwargs)
            self.assertEqual(InventoryReportRow.objects.count(), 1)
