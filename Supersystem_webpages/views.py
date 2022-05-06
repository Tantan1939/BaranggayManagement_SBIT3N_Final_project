from ast import Pass
from email.mime import image
import re
import json
from tkinter.tix import Tree
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from . models import *
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
# Create your views here.


# ----- USER views ------------------------------------------------------------------------------------------------------


def user_not_loggedin(user):
    if user.is_authenticated:
        return False
    return True


def check_user_type_clientSide(user):
    if user.is_superuser:
        return False
    elif user.is_staff:
        return False
    elif user.is_anonymous:
        return True
    return True


def user_account_only(user):
    if user.is_authenticated:
        if user.is_superuser:
            return False
        return True
    return False


def user_image_name(request):
    if request.user.is_authenticated:
        if Account_details.objects.filter(Account_name=request.user).exists():
            navbar_user = Account_details.objects.select_related(
                None).get(Account_name__username=request.user.username)
            return navbar_user
        return None
    return None


def auto_create_user_details(user):
    user_details = Account_details.objects.create(Account_name=user)


@user_passes_test(check_user_type_clientSide, login_url='supersystem_webpages-superuser')
def index(request):

    a = List_of_questions.objects.values(
        'question', 'answer').order_by(Lower('question'))
    b = Brgy_photos.objects.select_related(None).get(description='brgy')
    c = Brgy_photos.objects.select_related(
        None).get(description='healthservices')
    d = Brgy_photos.objects.select_related(None).get(description='eservices')

    context = {
        'navbar_user': user_image_name(request),
        'a': a,
        'b': b,
        'c': c,
        'd': d,
    }

    return render(request, 'Supersystem_webpages/client_side/index.html', context)


@user_passes_test(user_not_loggedin, login_url='/')
def register_account_anyone(request):

    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                return HttpResponse('username')

            elif User.objects.filter(email=email).exists():
                return HttpResponse('email')

            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password1
                )
                user.save()
                auto_create_user_details(user)
                return HttpResponse('created')

        else:
            return HttpResponse('password')

    return render(request, 'Supersystem_webpages/account_registration.html')


@user_passes_test(user_account_only, login_url='/')
def update_account_details(request):
    context = {
        'navbar_user': user_image_name(request),
    }
    return render(request, 'Supersystem_webpages/client_side/update_profile.html', context)


@user_passes_test(user_account_only, login_url='/')
def func_update_account_details(request):
    if request.method == "POST":
        new_image = Account_details.objects.get(Account_name=request.user)
        new_image.Age = request.POST['user_age']
        new_image.Contact_number = request.POST['contact_number']
        new_image.save()
        return HttpResponse('updated')
    return None


@user_passes_test(user_account_only, login_url='/')
def func_get_account_details(request):
    a = Account_details.objects.values('Account_name__username').get(
        Account_name=request.user)
    b = Account_details.objects.select_related(
        None).get(Account_name=request.user)

    if b.Age is None:
        b.Age = ""

    if b.Contact_number is None:
        b.Contact_number = ""

    context = {
        'a': a,
        'b': b.Profile_picture.url,
        'c': b.Age,
        'd': b.Contact_number,
    }
    return JsonResponse(context, safe=False)


def func_update_profile_image(request):
    # if len(request.FILES) != 0:
    if request.method == "POST":
        new_image = Account_details.objects.get(Account_name=request.user)
        new_image.Profile_picture = request.FILES['profile_image']
        new_image.save()
        response_data = {
            'image_urls': new_image.Profile_picture.url,
        }
    return HttpResponse(json.dumps(response_data))


@user_passes_test(user_not_loggedin, login_url='/')
def login_page(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            if user.is_superuser:
                return HttpResponse('admin_index')
            return HttpResponse("client_index")
        return HttpResponse("incorrect")

    return render(request, 'Supersystem_webpages/login_page.html')


@login_required(login_url='supersystem_webpages-login')
def logout_btn(request):
    auth_logout(request)
    return redirect('supersystem_webpages-index', permanent=True)

# -----------------------------------------------------------------------------------------------------------------------

# ----- ADMIN views -----------------------------------------------------------------------------------------------------


def admin_only(user):
    if user.is_superuser:
        return True
    return False


@user_passes_test(admin_only, login_url='/')
def admin_index(request):
    return render(request, 'Supersystem_webpages/admin_side/index.html')


@user_passes_test(admin_only, login_url='/')
def view_residents(request):
    return render(request, 'Supersystem_webpages/admin_side/View_residents.html')

# -----------------------------------------------------------------------------------------------------------------------
