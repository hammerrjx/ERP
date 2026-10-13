from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("backend", "0055_user_employee_link_and_count_checker")]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="strategic_supplier",
            field=models.BooleanField(default=False),
        ),
    ]
