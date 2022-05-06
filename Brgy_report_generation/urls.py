from unicodedata import name
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='brgy_report_generation-index'),

    # admin urls
    path('brgy_report_generation_superuser/', include([
        path('', views.admin_index, name='brgy_report_generation_superuser-index'),
    ])),
]
