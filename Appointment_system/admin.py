from django.contrib import admin
from django.apps import apps
# Register your models here.

for model in apps.get_app_config('Appointment_system').models.values():
    admin.site.register(model)
