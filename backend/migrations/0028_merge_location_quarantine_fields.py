from django.db import migrations


def merge_quarantine_flags(apps, schema_editor):
    Location = apps.get_model("backend", "Location")
    Location.objects.filter(inspection_reject_return_only=True).update(quarantine_return=True)


class Migration(migrations.Migration):
    dependencies = [("backend", "0027_location_shipped_goods_account")]

    operations = [
        migrations.RunPython(merge_quarantine_flags, migrations.RunPython.noop),
        migrations.RemoveField(model_name="location", name="inspection_reject_return_only"),
    ]
