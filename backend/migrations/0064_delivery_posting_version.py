from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('backend', '0063_currency_source_object_currencyrate_end_rate_and_more')]
    operations = [migrations.AddField(model_name='deliveryorder', name='posting_version',
        field=models.PositiveIntegerField(default=0, editable=False))]
