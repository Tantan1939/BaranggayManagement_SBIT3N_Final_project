# Generated by Django 4.0.3 on 2022-04-18 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Health_services', '0015_seasonalservices_request_is_cancelled'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtest_request',
            name='Is_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]