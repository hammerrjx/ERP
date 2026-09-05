from django.db import migrations, models


def align_existing_source_objects(apps, schema_editor):
    GoodsReceipt = apps.get_model("backend", "GoodsReceipt")
    GoodsReceiptLine = apps.get_model("backend", "GoodsReceiptLine")
    GoodsReceipt.objects.filter(source_object="grn_mstr").update(source_object="prh_receiver")
    GoodsReceiptLine.objects.filter(source_object="grnd_det").update(source_object="prh_hist")


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0023_goodsreceipt_supplier_delivery_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goodsreceipt",
            name="source_object",
            field=models.CharField(default="prh_receiver", max_length=40),
        ),
        migrations.AlterField(
            model_name="goodsreceiptline",
            name="source_object",
            field=models.CharField(default="prh_hist", max_length=40),
        ),
        migrations.RunPython(align_existing_source_objects, migrations.RunPython.noop),
    ]
