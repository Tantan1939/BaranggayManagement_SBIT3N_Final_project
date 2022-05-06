from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'Record_management/Client_side/index.html')


def admin_index(request):
    return render(request, 'Record_management/Admin_side/index.html')
