"""Read only the selected materials; keep the existing live supply formulas."""
from django.db.models import Case, CharField, Count, F, Q, Subquery, Value, When
from backend.domain.inventory_analysis import InventoryAnalysisPart, InventoryAnalysisSnapshot
from backend.domain.inventory_reports import InventoryReportRow
from backend.domain.master_data import Material
from backend.live_inventory import live_batch, bulk_payload


def select_bulk(site, source):
    batch = live_batch() if source != 'dgyzx1' else None
    snapshots = InventoryAnalysisSnapshot.objects.defer('payload')
    snapshot = snapshots.filter(kind='localbulk', site=site).first() if batch else None
    snapshot = snapshot or snapshots.filter(kind='bulk', site=site).first()
    if snapshot:
        snapshot.report_source = 'local' if batch else 'coerp_dgyzx1'
    return snapshot, batch


def read_parts(snapshot, codes):
    parts = list(InventoryAnalysisPart.objects.filter(snapshot=snapshot,
        sort_code__in={code.casefold() for code in codes}).only('code', 'row', 'details', 'has_summary'))
    canonical = {p.code.casefold(): p.code for p in parts}
    codes = {canonical.get(code.casefold(), code) for code in codes}
    snapshot.payload = {'rows': [p.row for p in parts if p.has_summary],
                        'details': [d for p in parts for d in p.details]}
    return codes


def live_rows(snapshot, batch, codes):
    codes = read_parts(snapshot, codes)
    return bulk_payload(snapshot, batch, part=codes) if batch else snapshot.payload


def extra_rows(snapshot, batch):
    """Only calculate materials absent from the baseline, including newly created ones."""
    if not batch:
        return []
    baseline = InventoryAnalysisPart.objects.filter(snapshot=snapshot, has_summary=True).values('code')
    mapping = batch.manifest.get('material_codes', {})
    # Most imported material IDs retain their source codes. Only aliases need CASE.
    aliases = {pk: code for pk, code in mapping.items() if code}
    local_codes = dict(Material.objects.values_list('pk', 'code')) if aliases else {}
    changes = [When(pk=int(pk), then=Value(code)) for pk, code in aliases.items() if local_codes.get(int(pk)) != code]
    canonical = Case(*changes, default=F('code'), output_field=CharField()) if changes else F('code')
    codes = set(Material.objects.annotate(report_code=canonical).exclude(
        report_code__in=Subquery(baseline)).values_list('report_code', flat=True))
    codes.update(InventoryReportRow.objects.filter(batch=batch, kind='inventory', site=snapshot.site)
        .exclude(material_code__in=Subquery(baseline)).values_list('material_code', flat=True).distinct())
    codes.update(InventoryAnalysisPart.objects.filter(snapshot=snapshot, has_summary=False).values_list('code', flat=True))
    prior = {row['part'] for row in batch.manifest.get('local_contributions', {}).values() if row['site'] == snapshot.site}
    prior.difference_update(InventoryAnalysisPart.objects.filter(snapshot=snapshot, code__in=prior).values_list('code', flat=True))
    codes.update(prior)
    from backend.domain.purchase import PurchaseRequisitionLine
    from django.db.models.fields.json import KeyTextTransform
    from django.db.models.functions import Cast
    codes.update(PurchaseRequisitionLine.objects.filter(requisition__site=snapshot.site,
        line_status='', requisition__status__in=['draft', 'pending', 'approved', 'rejected'])
        .annotate(report_code=Cast(KeyTextTransform('pt_part', 'material_snapshot'), CharField()))
        .exclude(report_code__isnull=True).exclude(report_code='').exclude(report_code__in=Subquery(baseline))
        .values_list('report_code', flat=True).distinct())
    return live_rows(snapshot, batch, codes)['rows'] if codes else []


def page_rows(snapshot, batch, params, page, size):
    low, high = (params.get('material_' + suffix, '').strip().casefold() for suffix in ('from', 'to'))
    query = params.get('q', '').strip().casefold()
    reverse = params.get('direction', 'asc') == 'desc'
    base = InventoryAnalysisPart.objects.filter(snapshot=snapshot, has_summary=True)
    if low:
        base = base.filter(sort_code__gte=low)
    if high:
        base = base.filter(sort_code__lte=high)
    if query:
        base = base.filter(Q(name__icontains=query) | Q(specification__icontains=query))
    extras = [r for r in extra_rows(snapshot, batch) if
        (not low or r['tmp_part'].casefold() >= low) and (not high or r['tmp_part'].casefold() <= high)
        and (not query or any(query in str(r.get(k, '')).casefold() for k in ('pt_desc1', 'pt_spec')))]
    extras.sort(key=lambda r: r['tmp_part'].casefold(), reverse=reverse)
    start, end = (page - 1) * size, page * size
    selected, preceding = [], 0
    ranks = {}
    for offset in range(0, len(extras), 100):
        ranks.update(base.aggregate(**{f'r{i}': Count('pk', filter=Q(**{
            'sort_code__gt' if reverse else 'sort_code__lt': extras[i]['tmp_part'].casefold()}))
            for i in range(offset, min(offset + 100, len(extras)))}))
    for index, row in enumerate(extras):
        rank = ranks[f'r{index}'] + index
        if rank < start:
            preceding += 1
        elif rank < end:
            selected.append(row)
    offset = max(0, start - preceding)
    codes = list(base.order_by('-sort_code' if reverse else 'sort_code', 'code')
        .values_list('code', flat=True)[offset:offset + size - len(selected)])
    rows = live_rows(snapshot, batch, codes)['rows'] if codes else []
    rows.extend(selected)
    rows.sort(key=lambda r: r['tmp_part'].casefold(), reverse=reverse)
    return rows, base.count() + len(extras)
