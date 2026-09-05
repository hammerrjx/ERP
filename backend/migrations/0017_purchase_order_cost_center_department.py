import django.db.models.deletion
from django.db import migrations, models


def map_cost_centers(apps, schema_editor):
    Department = apps.get_model("backend", "Department")
    PurchaseOrder = apps.get_model("backend", "PurchaseOrder")
    departments = {code.upper(): pk for code, pk in Department.objects.values_list("code", "pk")}
    for order in PurchaseOrder.objects.exclude(cost_center_legacy=""):
        order.cost_center_id = departments.get(order.cost_center_legacy.strip().upper())
        if order.cost_center_id:
            order.save(update_fields=["cost_center"])


class Migration(migrations.Migration):
    dependencies = [("backend", "0016_sales_returns")]

    operations = [
        migrations.RenameField(
            model_name="purchaseorder", old_name="cost_center", new_name="cost_center_legacy",
        ),
        migrations.AddField(
            model_name="purchaseorder", name="cost_center",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="cost_center_purchase_orders", to="backend.department",
            ),
        ),
        migrations.RunPython(map_cost_centers, migrations.RunPython.noop),
        migrations.RemoveField(model_name="purchaseorder", name="cost_center_legacy"),
    ]
