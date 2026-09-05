from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def backfill_address_audit(apps, schema_editor):
    CustomerAddress = apps.get_model("backend", "CustomerAddress")
    now = timezone.now()
    CustomerAddress.objects.filter(created_at__isnull=True).update(created_at=now)
    CustomerAddress.objects.filter(updated_at__isnull=True).update(updated_at=now)


class Migration(migrations.Migration):
    dependencies = [("backend", "0036_paymentmethod_partner_payment_method_master")]

    operations = [
        migrations.AddField("customeraddress", "created_by", models.CharField(blank=True, max_length=64)),
        migrations.AddField("customeraddress", "created_at", models.DateTimeField(null=True)),
        migrations.AddField("customeraddress", "updated_by", models.CharField(blank=True, max_length=64)),
        migrations.AddField("customeraddress", "updated_at", models.DateTimeField(null=True)),
        migrations.AddField("customeraddress", "source_object", models.CharField(default="ca_mstr", max_length=40)),
        migrations.AddField("customeraddress", "source_key", models.CharField(blank=True, max_length=160)),
        migrations.AddField("salesquote", "address_code", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="sales_quotes", to="backend.customeraddress")),
        migrations.AddField("salesquote", "address_snapshot", models.CharField(blank=True, max_length=240)),
        migrations.AddField("salesorder", "address_code", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="sales_orders", to="backend.customeraddress")),
        migrations.AddField("salesorder", "address_snapshot", models.CharField(blank=True, max_length=240)),
        migrations.RunPython(backfill_address_audit, migrations.RunPython.noop),
        migrations.AlterField("customeraddress", "created_at", models.DateTimeField(auto_now_add=True)),
        migrations.AlterField("customeraddress", "updated_at", models.DateTimeField(auto_now=True)),
    ]
