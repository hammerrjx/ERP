from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("backend", "0026_customer_material_links_and_audit")]

    operations = [
        migrations.AddField(
            model_name="location",
            name="shipped_goods_account",
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
