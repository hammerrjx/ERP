from decimal import Decimal
from django.db import migrations


def backfill(apps, schema_editor):
    Line = apps.get_model('backend', 'PurchaseOrderLine')
    Allocation = apps.get_model('backend', 'PurchaseOrderAllocation')
    for line in Line.objects.filter(source_requisition_line__isnull=False, allocation_managed=False).select_related(
            'source_requisition_line__requisition', 'source_supplier_quote', 'material__uom').iterator():
        req = line.source_requisition_line
        m, d = Decimal(1), Decimal(1)
        if line.uom_id != req.uom_id:
            quote = line.source_supplier_quote
            if not quote or quote.uom_rate_d <= 0:
                raise RuntimeError(f'采购行{line.pk}缺少单位换算，迁移已停止')
            m, d = quote.uom_rate_m, quote.uom_rate_d
        # Historical models deliberately bypass live save hooks: the existing applied
        # quantity already includes this order, and must not be applied a second time.
        Allocation.objects.create(line_id=line.pk, sequence=10, kind='1', requisition_line_id=req.pk,
            quantity=line.quantity, inventory_quantity=line.quantity*m/d,
            snapshot={'requisition_number': req.requisition.number, 'requisition_line_number': req.line_number,
                      'source_profile': req.requisition.source_profile, 'site': req.requisition.site},
            created_by=line.order.created_by)
        line.allocation_managed=True;line.uom_rate_m=m;line.uom_rate_d=d
        line.save(update_fields=['allocation_managed','uom_rate_m','uom_rate_d'])


class Migration(migrations.Migration):
    dependencies=[('backend','0067_purchase_workspace')]
    operations=[migrations.RunPython(backfill, migrations.RunPython.noop)]
