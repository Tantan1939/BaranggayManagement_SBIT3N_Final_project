from re import L
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'Brgy_document_issuance/Client_side/index.html')


def index_admin(request):
    return render(request, 'Brgy_document_issuance/Admin_side/index.html')
