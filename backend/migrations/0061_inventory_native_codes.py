from django.db import migrations


def native_codes(apps, schema_editor):
    Ledger = apps.get_model('backend', 'StockTransaction')
    rows = Ledger.objects.using(schema_editor.connection.alias)
    mapping = {'purchase_receipt': '120', 'purchase_return': '220', 'sales_delivery': '260',
               'transfer_in': '150', 'transfer_out': '250', 'count_adjustment': '310'}
    # Negative delivery notes remain type 260; independent return notes are 261.
    rows.filter(movement_type='sales_return', source_model='backend.deliveryorder').update(movement_type='260')
    rows.filter(movement_type='sales_return').update(movement_type='261')
    for old, new in mapping.items():
        rows.filter(movement_type=old).update(movement_type=new)
    for row in rows.filter(movement_type='reversal', reversal_of__isnull=False).select_related('reversal_of'):
        rows.filter(pk=row.pk).update(movement_type=row.reversal_of.movement_type)
    # Imported cutover balances retain the opening marker; they are not fresh receipts.


class Migration(migrations.Migration):
    dependencies = [('backend', '0060_inventory_analysis_snapshot')]
    operations = [migrations.RunPython(native_codes)]
