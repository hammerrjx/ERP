"""Ledger-local, explicit opt-in for the approved single-user test scope."""
from pathlib import Path

from django.conf import settings
from django.db import connection

from backend.domain.inventory_reports import InventoryReportBatch


def local_test_scope():
    batch = InventoryReportBatch.objects.filter(active=True, source='local').first()
    scope = (batch.manifest.get('trade_mrp_local_test') or {}) if batch else {}
    return batch, scope


def generation_readiness(site='1000'):
    batch, scope = local_test_scope()
    supported = connection.vendor == 'sqlite' and connection.settings_dict.get('OPTIONS', {}).get('transaction_mode') == 'IMMEDIATE'
    matches = bool(scope.get('database_path')) and str(Path(connection.settings_dict['NAME']).resolve()).casefold() == scope['database_path'].casefold()
    local = bool(scope.get('enabled') and matches and supported and site == scope.get('site') == '1000')
    enabled = supported and site == '1000' and (local or settings.ERP_TRADE_MRP_GENERATION_ENABLED)
    return {'enabled': bool(enabled), 'local_test': local,
        'label': '本机测试账套 · 当前本地数据库' if local else '贸易MRP',
        'baseline_at': scope.get('baseline_at', '') if local else '',
        'scope_version': scope.get('version', '') if local else '',
        'message': '本地测试生成已启用；源数据基准已冻结，结果不代表源库实时建议。' if local else
            ('当前账套已启用生成。' if enabled else '当前账套未启用生成或运行环境不符合条件。'),
        'excluded_materials': scope.get('excluded_materials', []) if local else [],
        'batch_id': batch.pk if batch else None}


def material_scope_issues(material, scope):
    if not scope.get('enabled'):
        return []
    reasons = scope.get('blocked_materials', {}).get(material.code, [])
    return [f'冻结源基准存在贸易外或归属不明贡献：{reason}；本期排除该物料' for reason in reasons]
