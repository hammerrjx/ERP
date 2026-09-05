from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [("importing", "0002_erpimportprofile")]
    operations = [migrations.AddConstraint(
        model_name="erpimportprofile",
        constraint=models.UniqueConstraint(condition=Q(("enabled", True), ("is_default", True)), fields=("is_default",), name="uniq_enabled_default_import_profile"),
    )]
