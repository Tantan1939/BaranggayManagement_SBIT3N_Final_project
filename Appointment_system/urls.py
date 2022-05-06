from unicodedata import name
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='Appointment_system-index'),

    # admin urls
    path('Appointment_system_superuser/', include([
        path('', views.index_admin, name='Appointment_system_superuser-index'),
    ])),
]
