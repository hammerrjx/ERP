import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("importing", "0001_initial")]
    operations = [migrations.CreateModel(
        name="ErpImportProfile",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=80)),
            ("source_database", models.CharField(default="coerp_dgyzx1", max_length=128)),
            ("source_catalog", models.CharField(default="coerp_base", max_length=128)),
            ("source_view", models.CharField(default="V_AI_PT_MSTR", max_length=128)),
            ("source_company_column", models.CharField(default="coerp_dgyzx1", max_length=128)),
            ("enabled", models.BooleanField(default=True)),
            ("is_default", models.BooleanField(default=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("company", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="erp_import_profiles", to="backend.company")),
        ],
        options={"ordering": ("-is_default", "id")},
    )]
