from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'Appointment_system/Client_side/index.html')


def index_admin(request):
    return render(request, 'Appointment_system/Admin_side/index.html')
