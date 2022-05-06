from unicodedata import name
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='record_management-index'),

    # admin urls
    path('record_management_superuser/', include([
        path('', views.admin_index, name='record_management_superuser-index'),
    ])),
]
