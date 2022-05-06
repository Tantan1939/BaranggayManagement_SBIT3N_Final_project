from unicodedata import name
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='brgy_document_issuance-index'),

    # admin urls
    path('brgy_document_issuance_superuser/', include([
        path('', views.index_admin, name='brgy_document_issuance_superuser-index'),
    ])),
]
