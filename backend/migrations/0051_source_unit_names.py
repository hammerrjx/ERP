from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0050_warehouse_documents"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uom",
            name="name",
            field=models.CharField(max_length=32),
        ),
    ]
