from collections import defaultdict
from django.db import models, transaction


class InventoryAnalysisSnapshot(models.Model):
    kind = models.CharField(max_length=10)
    site = models.CharField(max_length=30)
    period = models.CharField(max_length=7, blank=True)
    captured_at = models.DateTimeField(auto_now=True)
    payload = models.JSONField(default=dict)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('kind', 'site', 'period'), name='unique_inventory_analysis')]

    def save(self, *args, **kwargs):
        rebuild = self.kind in {'bulk', 'localbulk'} and (not kwargs.get('update_fields') or 'payload' in kwargs['update_fields'])
        with transaction.atomic():
            super().save(*args, **kwargs)
            if rebuild:
                rebuild_parts(self, InventoryAnalysisPart)


class InventoryAnalysisPart(models.Model):
    snapshot = models.ForeignKey(InventoryAnalysisSnapshot, on_delete=models.CASCADE, related_name='parts')
    code = models.CharField(max_length=100)
    sort_code = models.CharField(max_length=100)
    name = models.CharField(max_length=255, blank=True)
    specification = models.TextField(blank=True)
    has_summary = models.BooleanField(default=True)
    row = models.JSONField(default=dict)
    details = models.JSONField(default=list)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('snapshot', 'code'), name='unique_analysis_part')]
        indexes = [models.Index(fields=('snapshot', 'sort_code'), name='analysis_part_page'),
            models.Index(fields=('snapshot', 'has_summary', 'sort_code', 'code'), name='analysis_part_summary')]


def rebuild_parts(snapshot, model):
    """Publish an indexed copy when a capture is saved, never during a read request."""
    rows = {r['tmp_part']: r for r in snapshot.payload.get('rows', [])}
    details = defaultdict(list)
    for detail in snapshot.payload.get('details', []):
        details[detail['part']].append(detail)
    model.objects.filter(snapshot_id=snapshot.pk).delete()
    model.objects.bulk_create([model(snapshot_id=snapshot.pk, code=code, sort_code=code.casefold(),
        name=rows.get(code, {}).get('pt_desc1') or '', specification=rows.get(code, {}).get('pt_spec') or '',
        has_summary=code in rows, row=rows.get(code, {}), details=details[code])
        for code in rows.keys() | details.keys()], batch_size=100)
