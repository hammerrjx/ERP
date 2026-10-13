from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def map_legacy_checkers(apps, schema_editor):
    Employee = apps.get_model("backend", "Employee")
    InventoryDocument = apps.get_model("backend", "InventoryDocument")
    UserEmployeeLink = apps.get_model("backend", "UserEmployeeLink")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    employees = {code.strip(): pk for pk, code in Employee.objects.values_list("pk", "code") if code and code.strip()}
    for document in InventoryDocument.objects.exclude(checker=""):
        code = document.checker.strip()
        employee_id = employees.get(code)
        if employee_id:
            document.checker_employee_id = employee_id
            document.save(update_fields=["checker_employee"])
            continue
        payload = dict(document.source_payload or {})
        payload.setdefault("legacy_checker_unmapped", code)
        document.source_payload = payload
        document.save(update_fields=["source_payload"])

    # usr_mstr.usr_user is the legacy account identifier. Preserve any manually
    # maintained association and only fill gaps where the identifier is unique.
    linked_users = set(UserEmployeeLink.objects.values_list("user_id", flat=True))
    linked_employees = set(UserEmployeeLink.objects.values_list("employee_id", flat=True))
    for user_id, username in User.objects.values_list("pk", "username"):
        employee_id = employees.get((username or "").strip())
        if employee_id and user_id not in linked_users and employee_id not in linked_employees:
            UserEmployeeLink.objects.create(user_id=user_id, employee_id=employee_id)
            linked_employees.add(employee_id)


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0054_warehouse_line_audit"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="agent_code",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="employee",
            name="allowed_ip",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="employee",
            name="other_contact",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="employee",
            name="partner_code",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="employee",
            name="user_type",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.CreateModel(
            name="UserEmployeeLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="account_link", to="backend.employee")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="employee_link", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("user__username",)},
        ),
        migrations.AddField(
            model_name="inventorydocument",
            name="checker_employee",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="+", to="backend.employee"),
        ),
        migrations.RunPython(map_legacy_checkers, migrations.RunPython.noop),
        migrations.RemoveField(model_name="inventorydocument", name="checker"),
        migrations.RenameField(model_name="inventorydocument", old_name="checker_employee", new_name="checker"),
        migrations.AlterField(
            model_name="inventorydocument",
            name="checker",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="inventory_counts", to="backend.employee"),
        ),
    ]
