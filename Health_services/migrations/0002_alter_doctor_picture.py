# Generated by Django 4.0.3 on 2022-04-06 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Health_services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='Picture',
            field=models.ImageField(default='Default_doctor.png', upload_to='Health_services-Doctors_profile_images'),
        ),
    ]
