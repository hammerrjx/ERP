from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("backend", "0043_salesorder_consignment_and_more")]

    operations = [
        migrations.AlterField(
            model_name="deliveryorderline",
            name="actual_quantity",
            field=models.DecimalField(decimal_places=6, max_digits=18),
        ),
        migrations.AlterField(
            model_name="deliveryorderline",
            name="actual_spare_quantity",
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name="deliveryorderline",
            name="srm_quantity",
            field=models.DecimalField(decimal_places=6, max_digits=18),
        ),
        migrations.AddField(
            model_name="deliveryorderline",
            name="notes",
            field=models.CharField(blank=True, max_length=240),
        ),
    ]
