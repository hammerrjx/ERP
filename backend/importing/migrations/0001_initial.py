import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("backend", "0022_partner_field_alignment")]

    operations = [
        migrations.CreateModel(
            name="MaterialImportBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_file", models.FileField(upload_to="imports/materials/%Y/%m/%d")),
                ("original_filename", models.CharField(max_length=255)),
                ("default_tax_code", models.CharField(blank=True, max_length=32)),
                ("status", models.CharField(choices=[("preview", "待确认"), ("imported", "已导入"), ("failed", "导入失败")], default="preview", max_length=16)),
                ("total_rows", models.PositiveIntegerField(default=0)),
                ("valid_rows", models.PositiveIntegerField(default=0)),
                ("error_rows", models.PositiveIntegerField(default=0)),
                ("imported_rows", models.PositiveIntegerField(default=0)),
                ("created_by", models.CharField(blank=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("confirmed_by", models.CharField(blank=True, max_length=64)),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
        migrations.CreateModel(
            name="MaterialImportRow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("row_number", models.PositiveIntegerField()),
                ("source_data", models.JSONField(default=dict)),
                ("normalized_data", models.JSONField(default=dict)),
                ("allocated_code", models.CharField(blank=True, max_length=40)),
                ("status", models.CharField(choices=[("valid", "可导入"), ("error", "有错误"), ("imported", "已导入")], default="error", max_length=16)),
                ("errors", models.JSONField(default=list)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rows", to="importing.materialimportbatch")),
                ("material", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="import_rows", to="backend.material")),
            ],
            options={"ordering": ("row_number",)},
        ),
        migrations.AddConstraint(
            model_name="materialimportrow",
            constraint=models.UniqueConstraint(fields=("batch", "row_number"), name="uniq_material_import_row"),
        ),
    ]
