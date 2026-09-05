from django.db import migrations, models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Migration(migrations.Migration):
    dependencies = [("backend", "0031_businessgroup_supplierquote_business_group")]

    operations = [
        migrations.AddField(
            model_name="salesorder", name="tax_included",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="salesorder", name="tax_rate",
            field=models.DecimalField(
                decimal_places=8, default=Decimal("0"), max_digits=19,
                validators=[MinValueValidator(Decimal("0"))],
            ),
        ),
    ]
