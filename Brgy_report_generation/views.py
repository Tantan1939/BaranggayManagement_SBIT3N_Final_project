from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'Brgy_report_generation/Client_side/index.html')


def admin_index(request):
    return render(request, 'Brgy_report_generation/Admin_side/index.html')
