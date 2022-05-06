# Generated by Django 4.0.3 on 2022-03-20 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Supersystem_webpages', '0002_account_details_contact_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brgy_photos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='Brgy_images')),
                ('Updated', models.DateTimeField(auto_now=True)),
                ('Created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='List_of_questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('Updated', models.DateTimeField(auto_now=True)),
                ('Created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]