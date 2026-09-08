from decimal import Decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("backend", "0048_delivery_source_quantity_precision")]

    operations = [
        migrations.AlterField(
            model_name="salesorderline",
            name="quantity",
            field=models.DecimalField(max_digits=19, decimal_places=8,
                                      validators=[django.core.validators.MinValueValidator(Decimal("0"))]),
        ),
    ]
