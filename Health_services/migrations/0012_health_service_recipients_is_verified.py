# Generated by Django 4.0.3 on 2022-04-12 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Health_services', '0011_alter_health_service_recipients_user_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='health_service_recipients',
            name='Is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
