# Generated by Django 4.0.3 on 2022-04-17 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Health_services', '0014_remove_seasonal_health_service_available_today'),
    ]

    operations = [
        migrations.AddField(
            model_name='seasonalservices_request',
            name='Is_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
