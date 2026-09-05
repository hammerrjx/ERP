from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("backend", "0021_location_attribute")]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="buyer",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="partner",
            name="copper_currency",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="partner",
            name="copper_origin",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="partner",
            name="notes",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
