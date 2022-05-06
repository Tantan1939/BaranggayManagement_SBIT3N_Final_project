from codecs import namereplace_errors
from distutils.core import run_setup
from inspect import getcallargs
from operator import truediv
from queue import Empty
import re
from turtle import title
from types import NoneType
from django import http
from django.shortcuts import render, redirect
from Supersystem_webpages.views import check_user_type_clientSide, user_account_only, user_image_name, auto_create_user_details, admin_only
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from . models import *
from datetime import date, time, datetime
import datetime
import json
from django.http import HttpResponsePermanentRedirect, JsonResponse, HttpResponse, FileResponse
from django.db.models import F, Q, Count, Sum, CharField, Avg, Max, FloatField, Min
from django.db.models.functions import Lower
import io
from reportlab.platypus import PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


# ---------- ADMIN SIDE -----------------------------------------------------------------------------

@user_passes_test(admin_only, login_url='/')
def admin_index(request):
    a = LabTest_request.objects.values('Name__username', 'Beneficiary_name', 'Requested_labTest__Title', 'Requested_labTest__Fees',
                                       'Appointment_date', 'created').filter(Appointment_date__gte=datetime.date.today(), Is_cancelled=False).order_by('Appointment_date')

    a2 = LabTest_request.objects.values('Name__username', 'Beneficiary_name', 'Requested_labTest__Title', 'Requested_labTest__Fees',
                                        'Appointment_date', 'created').exclude(Q(Appointment_date__gte=datetime.date.today()) | Q(Is_cancelled=False)).order_by('created')

    b = SeasonalServices_request.objects.values('Name__username', 'Beneficiary_name', 'Service_type__Title', 'Appointment_date', 'created').filter(
        Appointment_date__gte=datetime.date.today(), Is_cancelled=False).order_by('Appointment_date')

    b2 = SeasonalServices_request.objects.values('Name__username', 'Beneficiary_name', 'Service_type__Title', 'Appointment_date', 'created').exclude(
        Q(Appointment_date__gte=datetime.date.today()) | Q(Is_cancelled=True)).order_by('created')

    context = {
        'incoming_LabTest_request': a,
        'previous_LabTest_request': a2,
        'incoming_SeasonalServices_request': b,
        'previous_SeasonalServices_request': b2,
        'segment': 'labtest_appointment'
    }

    return render(request, 'Health_services/admin_side/Labtest_appointment.html', context)


@user_passes_test(admin_only, login_url='/')
def generate_labtest_copies(request):
    # Create Bytestream buffer
    buf = io.BytesIO()

    # Create a canvas - size of a bond paper
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

    # Create a text-object: what to put in the canvas
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    to_pdf = LabTest_request.objects.filter(
        Appointment_date=datetime.date.today()).exclude(Is_cancelled=True).order_by('Appointment_date')
    count_this_to_pdf = LabTest_request.objects.filter(
        Appointment_date=datetime.date.today()).exclude(Is_cancelled=True).order_by('Appointment_date').count()

    getcurrent_date = "{:%b %d, %Y}".format(datetime.date.today())

    if count_this_to_pdf < 1:
        textob.textLine(" ")
        textob.textLine(" There are no Appointment for today ")
        textob.textLine(" Generated on: " + getcurrent_date)
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)
        return FileResponse(buf, filename='Labtest_copies.pdf')

    lines = []
    lines.append("Laboratory Test Requests for today")
    lines.append("Generated on: " + getcurrent_date)
    lines.append(" ")

    for line in lines:
        textob.textLine(line)
    c.drawText(textob)

    break_page_after_this = 0
    counter_terrorist = 0
    textobs = c.beginText()
    textobs.setTextOrigin(inch, inch)
    textobs.setFont("Helvetica", 14)
    textobs.textLine(" ")
    textobs.textLine(" ")
    textobs.textLine(" ")

    for each_request in to_pdf:
        counter_terrorist += 1
        textobs.textLine("Name: " + each_request.Name.username)
        textobs.textLine("Beneficiary Name: " +
                         each_request.Beneficiary_name)
        textobs.textLine("Requested Lab-Test: " +
                         each_request.Requested_labTest.Title)
        textobs.textLine("Appointment Date: " +
                         "{:%b %d, %Y}".format(each_request.Appointment_date))
        textobs.textLine(" ")

        break_page_after_this += 1
        if break_page_after_this == 8:
            break_page_after_this = 0
            c.drawText(textobs)
            # textobs = None
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

        if counter_terrorist == count_this_to_pdf and count_this_to_pdf % 2 > 0 and count_this_to_pdf > 8:
            break_page_after_this = 0
            c.drawText(textobs)
            # textobs = None
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

        if counter_terrorist == count_this_to_pdf and count_this_to_pdf % 2 == 0 and count_this_to_pdf > 8:
            break_page_after_this = 0
            c.drawText(textobs)
            # textobs = None
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

        if break_page_after_this == count_this_to_pdf and count_this_to_pdf < 8:
            break_page_after_this = 0
            c.drawText(textobs)
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

    c.save()
    buf.seek(0)

    return FileResponse(buf, filename='Labtest_copies.pdf')


@user_passes_test(admin_only, login_url='/')
def generate_seasonal_requests_copies(request):
    # Create Bytestream buffer
    buf = io.BytesIO()

    # Create a canvas - size of a bond paper
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

    # Create a text-object: what to put in the canvas
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    to_pdf = SeasonalServices_request.objects.filter(
        Appointment_date=datetime.date.today()).exclude(Is_cancelled=True).order_by('Appointment_date')
    count_this_to_pdf = SeasonalServices_request.objects.filter(
        Appointment_date=datetime.date.today()).exclude(Is_cancelled=True).order_by('Appointment_date').count()

    getcurrent_date = "{:%b %d, %Y}".format(datetime.date.today())

    if count_this_to_pdf < 1:
        textob.textLine(" ")
        textob.textLine(" There are no requests for today ")
        textob.textLine(" Generated on: " + getcurrent_date)
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)
        return FileResponse(buf, filename='health_Service_requests_copy.pdf')

    lines = []
    lines.append("Health service Requests for today")
    lines.append("Generated on: " + getcurrent_date)
    lines.append(" ")

    for line in lines:
        textob.textLine(line)
    c.drawText(textob)

    break_page_after_this = 0
    counter_terrorist = 0
    textobs = c.beginText()
    textobs.setTextOrigin(inch, inch)
    textobs.setFont("Helvetica", 14)
    textobs.textLine(" ")
    textobs.textLine(" ")
    textobs.textLine(" ")

    for each_request in to_pdf:
        counter_terrorist += 1
        textobs.textLine("Name: " + each_request.Name.username)
        textobs.textLine("Beneficiary Name: " +
                         each_request.Beneficiary_name)
        textobs.textLine("Type of service: " +
                         each_request.Service_type.Title)
        textobs.textLine("Appointment Date: " +
                         "{:%b %d, %Y}".format(each_request.Appointment_date))
        textobs.textLine(" ")

        break_page_after_this += 1
        if break_page_after_this == 8:
            break_page_after_this = 0
            c.drawText(textobs)
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

        if counter_terrorist == count_this_to_pdf and count_this_to_pdf % 2 > 0 and count_this_to_pdf > 8:
            break_page_after_this = 0
            c.drawText(textobs)
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

        if counter_terrorist == count_this_to_pdf and count_this_to_pdf % 2 == 0 and count_this_to_pdf > 8:
            break_page_after_this = 0
            c.drawText(textobs)
            # textobs = None
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

        if break_page_after_this == count_this_to_pdf and count_this_to_pdf < 8:
            break_page_after_this = 0
            c.drawText(textobs)
            textobs = c.beginText()
            textobs.setTextOrigin(inch, inch)
            textobs.setFont("Helvetica", 14)
            c.showPage()

    c.save()
    buf.seek(0)

    return FileResponse(buf, filename='health_Service_requests_copy.pdf')


@user_passes_test(admin_only, login_url='/')
def Lab_test(request):
    context = {
        "title": "Laboratory_Tests",
        "segment": "Laboratory_Tests",
    }
    return render(request, 'Health_services/admin_side/Laboratory_test.html', context)


@user_passes_test(admin_only, login_url='/')
def Create_Lab_Test(request):
    if request.method == "POST":
        get_title = request.POST.get('lab_title')
        get_description = request.POST.get('lab_desc')
        get_fees = request.POST.get('lab_fees')
        get_fees = int(get_fees)
        get_Need_appointment = request.POST.get('lab_bool')
        bool_appt = True if get_Need_appointment == "True" else False

        if Laboratory_test.objects.filter(Title__iexact=get_title, Is_available=True).exists():
            return HttpResponse("xExists")
        elif Laboratory_test.objects.filter(Title__iexact=get_title, Is_available=False).exists():
            Laboratory_test.objects.filter(
                Title__iexact=get_title).update(Title=get_title, Description=get_description, Fees=get_fees, Is_available=True, Need_appointment=bool_appt)
            return HttpResponse(get_title + " is created again.")
        else:
            Laboratory_test.objects.create(Title=get_title, Description=get_description,
                                           Fees=get_fees, Is_available=True, Need_appointment=bool_appt)
            return HttpResponse(get_title + " is successfully added.")
    return None


@user_passes_test(admin_only, login_url='/')
def get_Lab_test(request):
    a = Laboratory_test.objects.values(
        'id', 'Title', 'Description', 'Fees', 'Need_appointment').exclude(Is_available=False).order_by(Lower('Title'))

    context = {
        'list_of_Labtest': list(a),
    }
    return JsonResponse(context)


@user_passes_test(admin_only, login_url='/')
def Get_single_labTest(request, pk):

    if Laboratory_test.objects.filter(id=pk, Is_available=True).exists():
        get_responses = Laboratory_test.objects.select_related(None).get(id=pk)
        context = {
            'id': get_responses.id,
            'a': get_responses.Title,
            'b': get_responses.Description,
            'c': get_responses.Fees,
            'd': get_responses.Need_appointment,
        }
        return JsonResponse(context)
    return HttpResponse("Laboratory Test no longer exist.")


@user_passes_test(admin_only, login_url='/')
def Update_lab_test_info(request):
    if request.method == "POST":
        labTEST_id = request.POST.get('LabTEST_ID')
        labTEST_id = int(labTEST_id)
        labtestName = request.POST.get('labtestName')
        Desc = request.POST.get('Desc')
        fees = request.POST.get('fees')
        fees = int(fees)
        lab_bool = request.POST.get('lab_bool')

        if Laboratory_test.objects.filter(id=labTEST_id, Title=labtestName, Is_available=True).exists():
            if Laboratory_test.objects.filter(id=labTEST_id, Title=labtestName, Description=Desc, Fees=fees, Is_available=True, Need_appointment=lab_bool).exists():
                return HttpResponse('No new information saved.')
            Laboratory_test.objects.filter(id=labTEST_id, Title=labtestName, Is_available=True).update(
                Title=labtestName, Description=Desc, Fees=fees, Need_appointment=lab_bool)
            return HttpResponse('LabTest Updated Successfully')
        return HttpResponse('Object does not exist.')
    return None


@user_passes_test(admin_only, login_url='/')
def Del_lab_test_info(request):
    if request.method == "POST":
        labtestID = request.POST.get('labtestID')
        labtestID = int(labtestID)

        if Laboratory_test.objects.filter(id=labtestID, Is_available=True).exists():
            Laboratory_test.objects.filter(
                id=labtestID, Is_available=True).update(Is_available=False)
            return HttpResponse("Deleted Successfully.")
        return HttpResponse('Laboratory Test no longer exist.')
    return None


@user_passes_test(admin_only, login_url='/')
def list_of_doctors(request):
    context = {
        "title": "List of Doctors",
        "segment": "List of Doctors"
    }

    return render(request, 'Health_services/admin_side/List_of_doctors.html', context)


@user_passes_test(admin_only, login_url='/')
def get_list_of_doctors(request):

    get_imgs = Doctor.objects.filter(Still_active=True).order_by(Lower('Name'))

    context = {
        "getimgs": [getimgs.serialize() for getimgs in get_imgs],
    }

    return JsonResponse(context, safe=False)


@user_passes_test(admin_only, login_url='/')
def get_doctor_name_only(request, pk):
    if Doctor.objects.filter(id=pk, Still_active=True).exists():
        a = Doctor.objects.select_related(None).get(id=pk)
        return HttpResponse(a.Name)
    return HttpResponse('')


@user_passes_test(admin_only, login_url='/')
def Del_doctor(request):
    if request.method == "POST":
        doctor_id = request.POST.get('DoctorID')
        doctor_id = int(doctor_id)
        doctor_name = request.POST.get('DoctorName')
        if Doctor.objects.filter(id=doctor_id, Still_active=True).exists():
            Doctor.objects.filter(id=doctor_id, Still_active=True).update(
                Still_active=False)
            return HttpResponse(doctor_name + " is Deleted.")
        return HttpResponse('Object no longer exist.')
    return None


@user_passes_test(admin_only, login_url='/')
def Create_doctor(request):
    if request.method == "POST":
        Doc_name = request.POST.get('Doc_name')
        Doc_age = request.POST.get('Doc_age')
        Doc_contactnum = request.POST.get('Doc_contactnum')
        Specialization = request.POST.get('Specialization')

        try:
            Specialization = int(Specialization)
            Doc_age = int(Doc_age)
            Doc_contactnum = int(Doc_contactnum)
            if Doctors_specialty.objects.filter(id=Specialization, Is_visible=True).exists():
                if verify_doctor_age(request, Doc_age):
                    if verify_doctor_contactnum(request, Doc_contactnum):

                        # Int to string
                        Doc_contactnum = str(Doc_contactnum)

                        # Declare an empty list
                        this_list = []

                        # Declare an empty string
                        new_doc_contact_num = ""

                        # Append each string to a list(list of strings)
                        for each_str in Doc_contactnum:
                            this_list.append(each_str)

                        this_list.insert(0, '6')
                        this_list.insert(1, '3')

                        # list to str
                        for obj in this_list:
                            new_doc_contact_num += obj

                        get_doctor_spec_obj = Doctors_specialty.objects.get(
                            id=Specialization)
                        if Doctor.objects.filter(Name__iexact=Doc_name, Still_active=True).exists():
                            return HttpResponse("exist")
                        elif Doctor.objects.filter(Name__iexact=Doc_name, Still_active=False).exists():
                            Doctor.objects.filter(Name__iexact=Doc_name, Still_active=False).update(
                                Name=Doc_name, Age=Doc_age, Contact_number=new_doc_contact_num, Specialty=get_doctor_spec_obj, Still_active=True)
                            return HttpResponse(Doc_name + " is created again.")
                        else:
                            Doctor.objects.create(Name=Doc_name, Age=Doc_age, Contact_number=new_doc_contact_num,
                                                  Specialty=get_doctor_spec_obj, Still_active=True)
                            return HttpResponse(Doc_name + " is successfully created.")
                    return HttpResponse('xCnum')
                return HttpResponse('xAge')
            return HttpResponse('xSpec')
        except:
            return HttpResponse('xEverything')
    return HttpResponse('')


@user_passes_test(admin_only, login_url='/')
def verify_doctor_age(request, doc_age):
    if doc_age < 18 or doc_age > 80:
        return False
    return True


@user_passes_test(admin_only, login_url='/')
def verify_doctor_contactnum(request, doc_num):
    if (len(str(doc_num))) == 10:

        doc_num = str(doc_num)
        this_list = []
        for obj in doc_num:
            this_list.append(obj)

        if this_list[0] == '9':
            return True
        return False
    return False


@user_passes_test(admin_only, login_url='/')
def get_specialization(request):
    doctor_specialization = Doctors_specialty.objects.values(
        'id', 'Title').exclude(Is_visible=False)

    context = {
        "doctor_specialization": list(doctor_specialization),
    }

    return JsonResponse(context)


@user_passes_test(admin_only, login_url='/')
def get_all_specialization(request):
    doctor_specialization = Doctors_specialty.objects.values('id', 'Title')

    context = {
        "doctor_specialization": list(doctor_specialization),
    }

    return JsonResponse(context)


@user_passes_test(admin_only, login_url='/')
def get_single_doctor_info(request, pk):

    if Doctor.objects.filter(id=pk, Still_active=True).exists():
        return_doctor_infos = Doctor.objects.filter(id=pk)
        return JsonResponse([doctor_get_infos.edit_serialize() for doctor_get_infos in return_doctor_infos], safe=False)
    return HttpResponse('')


@user_passes_test(admin_only, login_url='/')
def update_doctor_info(request):
    if request.method == "POST":

        doc_img = request.FILES.get('uploaded_imgs', False)
        Doctor_id = request.POST.get('Doctor_id')
        Doctor_name = request.POST.get('Doctor_name')
        Doctor_age = request.POST.get('Doctor_age')
        Doctor_contactnum = request.POST.get('Doctor_contactnum')
        Doctor_Specialization = request.POST.get('Doctor_Specialization')

        try:
            Doctor_id = int(Doctor_id)
            Doctor_age = int(Doctor_age)
            Doctor_Specialization = int(Doctor_Specialization)
            Doctor_contactnum = int(Doctor_contactnum)

            if Doctors_specialty.objects.filter(id=Doctor_Specialization).exists():
                get_spec = Doctors_specialty.objects.get(
                    id=Doctor_Specialization)
                if verify_doctor_age(request, Doctor_age):
                    if verify_doctor_contactnum(request, Doctor_contactnum):

                        # Int to string
                        Doctor_contactnum = str(Doctor_contactnum)

                        # Declare an empty list
                        this_list = []

                        # Declare an empty string
                        new_doc_contact_num = ""

                        # Append each string to a list(list of strings)
                        for each_str in Doctor_contactnum:
                            this_list.append(each_str)

                        this_list.insert(0, '6')
                        this_list.insert(1, '3')

                        # list to str
                        for obj in this_list:
                            new_doc_contact_num += obj

                        if doc_img is False:
                            if Doctor.objects.filter(id=Doctor_id, Still_active=True).exists():
                                if Doctor.objects.filter(id=Doctor_id, Name=Doctor_name).exists():

                                    if Doctor.objects.filter(id=Doctor_id, Name=Doctor_name, Age=Doctor_age, Contact_number=new_doc_contact_num, Specialty=get_spec).exists():
                                        return HttpResponse("No new information saved.")
                                    Doctor.objects.filter(id=Doctor_id).update(
                                        Age=Doctor_age, Contact_number=new_doc_contact_num, Specialty=get_spec)
                                    return HttpResponse(Doctor_name + " is updated successfully.")

                                elif Doctor.objects.filter(Name__iexact=Doctor_name).exclude(id=Doctor_id).exists():
                                    return HttpResponse('xName')

                                Doctor.objects.filter(id=Doctor_id).update(
                                    Name=Doctor_name, Age=Doctor_age, Contact_number=new_doc_contact_num, Specialty=get_spec)
                                return HttpResponse(Doctor_name + " is updated successfully.")

                            return HttpResponse('xExist')

                        if Doctor.objects.filter(id=Doctor_id, Still_active=True).exists():
                            if Doctor.objects.filter(id=Doctor_id, Name=Doctor_name).exists():
                                Doctor.objects.filter(id=Doctor_id).update(
                                    Age=Doctor_age, Contact_number=new_doc_contact_num, Specialty=get_spec)
                                zzz = Doctor.objects.get(id=Doctor_id)
                                zzz.Picture = request.FILES['uploaded_imgs']
                                zzz.save()
                                return HttpResponse(Doctor_name + " is updated successfully.")

                            elif Doctor.objects.filter(Name__iexact=Doctor_name).exclude(id=Doctor_id).exists():
                                return HttpResponse('xName')

                            Doctor.objects.filter(id=Doctor_id).update(
                                Name=Doctor_name, Age=Doctor_age, Contact_number=new_doc_contact_num, Specialty=get_spec)
                            up = Doctor.objects.get(id=Doctor_id)
                            up.Picture = request.FILES['uploaded_imgs']
                            up.save()
                            return HttpResponse(Doctor_name + " is updated successfully.")
                        return HttpResponse('xExist')
                    return HttpResponse('xCnum')
                return HttpResponse('xAge')
            return HttpResponse('xSpec')

        except:
            return HttpResponse('xEverything')
    return HttpResponse('')


@user_passes_test(admin_only, login_url='/')
def Doctors_credentials(request, pk):
    context = {
        "title": "Doctors Credentials",
        "pk": pk,
    }
    return render(request, 'Health_services/admin_side/Doctors_credentials.html', context)


@user_passes_test(admin_only, login_url='/')
def Add_credentials(request):
    if request.method == "POST":
        doctor_id = int(request.POST.get('doctor_id'))
        if Doctor.objects.filter(id=doctor_id, Still_active=True).exists():
            Doctors_credential.objects.create(
                Doctor_name=Doctor.objects.get(id=doctor_id),
                Title=request.POST.get('add_Title'),
                Description=request.POST.get('add_Description'),
                Awarded_date=request.POST.get('add_Awarded_date'),
                Certificate_image=request.FILES.get('add_uploaded_imgs'),
                Is_visible=True
            )
            return HttpResponse('')
        return HttpResponse('xDoc')
    return HttpResponse('xPOST')


@user_passes_test(admin_only, login_url='/')
def Get_credentials(request):
    if request.method == "POST":
        doc_id = int(request.POST.get('ids', False))

        if Doctor.objects.filter(id=doc_id, Still_active=True).exists():
            doctor_profile = Doctor.objects.select_related(
                None).filter(id=doc_id)
            if Doctors_credential.objects.filter(Doctor_name=doc_id, Is_visible=True).exists():
                credentials = Doctors_credential.objects.select_related(
                    None).filter(Doctor_name=doc_id, Is_visible=True)
                contexts = {
                    "doctor_profile": [doctor_profile.serialize() for doctor_profile in doctor_profile],
                    "credentials": [credentials.serialize() for credentials in credentials],
                }
                return JsonResponse(contexts, safe=False)

            context = {
                "doctor_profile": [doctor_profile.serialize() for doctor_profile in doctor_profile],
                "credentials": ""
            }
            return JsonResponse(context, safe=False)
        return HttpResponse('xDoc')


@user_passes_test(admin_only, login_url='/')
def get_single_credential(request, pk):
    credential_id = int(pk)
    if Doctor.objects.filter(doctors_credential__id=credential_id, Still_active=True).exists():
        if Doctors_credential.objects.filter(id=credential_id, Is_visible=True).exists():
            credential_info = Doctors_credential.objects.select_related(
                None).filter(id=credential_id)
            return JsonResponse([credential_info.serialize() for credential_info in credential_info], safe=False)
        return HttpResponse('xCredential')
    return HttpResponse('xDoc')


@user_passes_test(admin_only, login_url='/')
def Delete_this_credential(request):
    if request.method == "POST":
        delete_this_id = int(request.POST.get('delete_this_id'))
        doctor_this_id = int(request.POST.get('doctor_this_id'))

        if Doctor.objects.filter(id=doctor_this_id, Still_active=True).exists():
            if Doctors_credential.objects.filter(id=delete_this_id, Is_visible=True).exists():
                Doctors_credential.objects.filter(
                    id=delete_this_id).update(Is_visible=False)
                return HttpResponse('Credential is deleted successfully.')
            return HttpResponse('xCredential')
        return HttpResponse('xDoc')
    return HttpResponse('')


@user_passes_test(admin_only, login_url='/')
def Update_this_credential(request):
    if request.method == "POST":
        update_this_id = int(request.POST.get('update_this_id'))
        doctor_in_this_id = int(request.POST.get('doctor_in_this_id'))

        if Doctor.objects.filter(id=doctor_in_this_id, Still_active=True).exists():
            if Doctors_credential.objects.filter(id=update_this_id, Is_visible=True).exists():
                Doctors_credential.objects.filter(
                    id=update_this_id).update(
                        Title=request.POST.get('upd_Title'),
                        Description=request.POST.get('upd_Description'),
                        Awarded_date=request.POST.get('upd_Awarded_date'),
                )
                return HttpResponse('Credential is updated successfully.')
            return HttpResponse('xCredential')
        return HttpResponse('xDoc')
    return HttpResponse('')


@user_passes_test(admin_only, login_url='/')
def Free_checkup(request):
    context = {
        "title": "Free check_up",
        "segment": "Free check_up"
    }
    return render(request, 'Health_services/admin_side/Free_checkup.html', context)


@user_passes_test(admin_only, login_url='/')
def get_freecheckup_doctors(request):

    unassigned_doctors = Doctor.objects.filter(Still_active=True).annotate(entries=Count(
        'check_up')).filter(Q(entries__lt=1) | Q(check_up__Is_available=False)).order_by(Lower('Name'))

    assigned_doctors = Doctor.objects.filter(Still_active=True).annotate(entries=Count(
        'check_up')).filter(entries__gt=0, check_up__Is_available=True).order_by(Lower('Name'))

    context = {
        "unassigned_doctors": [unassigned_doctors.serialize() for unassigned_doctors in unassigned_doctors],
        "assigned_doctors": [assigned_doctors.serialize() for assigned_doctors in assigned_doctors],
    }

    return JsonResponse(context, safe=False)


@user_passes_test(admin_only, login_url='/')
def freecheckup_assign_doctor(request):
    if request.method == "POST":
        assign_this_id = int(request.POST.get('this_id'))
        if Doctor.objects.filter(id=assign_this_id, Still_active=True).exists():

            if Check_up.objects.filter(Assigned_doctor__id=assign_this_id, Is_available=False).exists():
                Check_up.objects.filter(
                    Assigned_doctor__id=assign_this_id).update(Is_available=True)
                return HttpResponse('Assigned again')
            Check_up.objects.create(
                Assigned_doctor=Doctor.objects.get(id=assign_this_id),
                Is_available=True
            )
            return HttpResponse('Assigned successfully')
        return HttpResponse('xDoc')
    return HttpResponse('xPost')


@user_passes_test(admin_only, login_url='/')
def freecheckup_unassign_doctor(request):
    if request.method == "POST":
        unassign_this_id = int(request.POST.get('unassign_this_id'))
        if Doctor.objects.filter(id=unassign_this_id, Still_active=True).exists():

            if Check_up.objects.filter(Assigned_doctor__id=unassign_this_id, Is_available=True).exists():
                Check_up.objects.filter(
                    Assigned_doctor__id=unassign_this_id).update(Is_available=False)
                return HttpResponse('Doctor unassigned successfully')
            return HttpResponse('xUnassign')
        return HttpResponse('xDoc')
    return HttpResponse('xPost')


@user_passes_test(admin_only, login_url='/')
def Seasonal_health_Services(request):
    context = {
        "title": "Seasonal Health Services",
        "segment": "Seasonal Health Services"
    }
    return render(request, 'Health_services/admin_side/Seasonal_health_Services.html', context)


@user_passes_test(admin_only, login_url='/')
def get_previous_health_services(request):
    get_this_lists = Seasonal_health_service.objects.filter(
        Is_deleted=False,
        Start_date__lt=datetime.date.today(),
        End_date__lt=datetime.date.today()).order_by('id')

    count_participants = Seasonal_health_service.objects.values('Title').filter(
        Start_date__lt=datetime.date.today(),
        End_date__lt=datetime.date.today()
    ).exclude(
        Is_deleted=True
    ).annotate(
        entries=Count('Service_type', filter=Q(
            Service_type__Is_cancelled=False))
    ).order_by('id')

    context = {
        "get_this_lists": [get_this_lists.serialize() for get_this_lists in get_this_lists],
        "count_participants": list(count_participants)
    }
    return JsonResponse(context, safe=False)


@user_passes_test(admin_only, login_url='/')
def get_ongoing_health_services(request):
    get_this_lists = Seasonal_health_service.objects.filter(
        Is_deleted=False,
        Start_date__lte=datetime.date.today(),
        End_date__gte=datetime.date.today()).order_by('id')

    count_participants = Seasonal_health_service.objects.values('Title').filter(
        Start_date__lte=datetime.date.today(),
        End_date__gte=datetime.date.today()
    ).exclude(
        Is_deleted=True
    ).annotate(
        entries=Count('Service_type', filter=Q(
            Service_type__Is_cancelled=False))
    ).order_by('id')

    context = {
        "get_this_lists": [get_this_lists.serialize() for get_this_lists in get_this_lists],
        "count_participants": list(count_participants)
    }
    return JsonResponse(context, safe=False)


@user_passes_test(admin_only, login_url='/')
def get_future_health_services(request):
    get_this_lists = Seasonal_health_service.objects.filter(
        Is_deleted=False,
        Start_date__gt=datetime.date.today(),
        End_date__gt=datetime.date.today()).order_by('-Start_date')
    return JsonResponse([get_this_lists.serialize() for get_this_lists in get_this_lists], safe=False)


@user_passes_test(admin_only, login_url='/')
def get_health_service_info(request, pk):
    if Seasonal_health_service.objects.filter(id=pk, Is_deleted=False).exists():
        get_info = Seasonal_health_service.objects.select_related(
            None).filter(id=pk)
        return JsonResponse([get_info.serialize() for get_info in get_info], safe=False)
    return HttpResponse('xService')


@user_passes_test(admin_only, login_url='/')
def Delete_this_previous_service(request):
    if request.method == "POST":
        this_id = int(request.POST.get('Delete_previous_Service_id'))
        if Seasonal_health_service.objects.filter(id=this_id, Is_deleted=False).exists():
            Seasonal_health_service.objects.filter(
                id=this_id).update(Is_deleted=True)
            return HttpResponse('Delete successfully')
        return HttpResponse('xService')
    return HttpResponse('xPost')


@user_passes_test(admin_only, login_url='/')
def Delete_this_future_service(request):
    if request.method == "POST":
        this_id = int(request.POST.get('Delete_future_Service_id'))
        if Seasonal_health_service.objects.filter(id=this_id, Is_deleted=False).exists():
            Seasonal_health_service.objects.filter(
                id=this_id).update(Is_deleted=True)
            return HttpResponse('Delete successfully')
        return HttpResponse('xService')
    return HttpResponse('xPost')


@user_passes_test(admin_only, login_url='/')
def add_this_service(request):
    if request.method == "POST":
        service_img = request.FILES.get('service_img', False)

        assigned_doctors = list(map(int, request.POST.getlist('assigned')))
        Start_date = datetime.datetime.strptime(
            request.POST.get('Start_date'), "%Y-%m-%d").date()
        End_date = datetime.datetime.strptime(
            request.POST.get('End_date'), "%Y-%m-%d").date()
        Open_time = request.POST.get('Open_time')
        Close_time = request.POST.get('Close_time')

        if Start_date > datetime.date.today() and End_date > datetime.date.today():
            if Start_date < End_date:
                if Close_time > Open_time:
                    if len(assigned_doctors) > 0:

                        get_this_doctors = Doctor.objects.filter(
                            pk__in=assigned_doctors)

                        create_this = Seasonal_health_service.objects.create(
                            Title=request.POST.get('Service_name'),
                            Goal=request.POST.get('Service_goals'),
                            Start_date=request.POST.get('Start_date'),
                            End_date=request.POST.get('End_date'),
                            Open_time=request.POST.get('Open_time'),
                            Close_time=request.POST.get('Close_time'),
                            Location=request.POST.get('Location'),
                            # Available_today=False,
                            Is_deleted=False,
                        )
                        create_this.Assigned_doctor.add(*get_this_doctors)

                        if service_img is not False:
                            create_this.Image = service_img
                            create_this.save()

                        return HttpResponse('')
                    else:
                        return HttpResponse('xAssigned')
                else:
                    return HttpResponse('xTime')
            else:
                return HttpResponse('xDate')
        else:
            return HttpResponse('xDate')


@user_passes_test(admin_only, login_url='/')
def Update_this_service(request):
    if request.method == "POST":

        assigned_doctors = list(
            map(int, request.POST.getlist('update_this_assigned')))
        Start_date = datetime.datetime.strptime(
            request.POST.get('upd_Start_date'), "%Y-%m-%d").date()
        End_date = datetime.datetime.strptime(
            request.POST.get('upd_End_date'), "%Y-%m-%d").date()
        Open_time = request.POST.get('upd_Open_time')
        Close_time = request.POST.get('upd_Close_time')
        service_id = int(request.POST.get('this_hidden_id'))

        if Seasonal_health_service.objects.filter(id=service_id, Is_deleted=False).exists():
            if Start_date > datetime.date.today() and End_date > datetime.date.today():
                if Start_date < End_date:
                    if Close_time > Open_time:
                        if len(assigned_doctors) > 0:

                            get_this_doctors = Doctor.objects.filter(
                                pk__in=assigned_doctors)

                            update_this = Seasonal_health_service.objects.filter(id=service_id).update(
                                Title=request.POST.get('upd_Service_name'),
                                Goal=request.POST.get('upd_Service_goals'),
                                Start_date=request.POST.get('upd_Start_date'),
                                End_date=request.POST.get('upd_End_date'),
                                Open_time=request.POST.get('upd_Open_time'),
                                Close_time=request.POST.get('upd_Close_time'),
                                Location=request.POST.get('upd_Location'),
                                # Available_today=False,
                                Is_deleted=False,
                            )

                            # update a manytomany field
                            update_this_doctors_Assigned = Seasonal_health_service.objects.get(
                                id=service_id)
                            update_this_doctors_Assigned.Assigned_doctor.clear()
                            update_this_doctors_Assigned.Assigned_doctor.add(
                                *get_this_doctors)

                            return HttpResponse('')
                        else:
                            return HttpResponse('xAssigned')
                    else:
                        return HttpResponse('xTime')
                else:
                    return HttpResponse('xDate')
            else:
                return HttpResponse('xDate')
        else:
            return HttpResponse('xService')


@user_passes_test(admin_only, login_url='/')
def Health_center_informations(request):
    context = {
        "title": "Health Center Informations",
        "segment": "Health Center Informations"
    }
    return render(request, 'Health_services/admin_side/Health_center_information.html', context)


@user_passes_test(admin_only, login_url='/')
def get_set_health_center_information(request):
    if request.method == "POST":
        this_id = int(request.POST.get('this_id'))
        upd_opentime = request.POST.get('upd_opentime')
        upd_closingtime = request.POST.get('upd_closingtime')
        upd_contactnum = request.POST.get('upd_contactnum')

        try:
            upd_contactnum = int(upd_contactnum)
            if Health_center_contactInformation.objects.filter(id=this_id).exists():
                if upd_closingtime <= upd_opentime:
                    return HttpResponse('xTime')
                if verify_doctor_contactnum(request, upd_contactnum):
                    # Int to string
                    upd_contactnum = str(upd_contactnum)

                    # Declare an empty list
                    this_list = []

                    # Declare an empty string
                    this_contact_num = ""

                    # Append each string to a list(list of strings)
                    for each_str in upd_contactnum:
                        this_list.append(each_str)

                    this_list.insert(0, '6')
                    this_list.insert(1, '3')

                    # list to str
                    for obj in this_list:
                        this_contact_num += obj

                    Health_center_contactInformation.objects.filter(id=this_id).update(
                        Name=request.POST.get('upd_name'),
                        Address=request.POST.get('upd_address'),
                        Contact_number=this_contact_num,
                        Email_address=request.POST.get('upd_email'),
                        Available_days=request.POST.get('upd_days'),
                        Open_time=request.POST.get('upd_opentime'),
                        Close_time=request.POST.get('upd_closingtime'),
                        Open_today=request.POST.get('status_today'),
                    )
                    return HttpResponse('')
                return HttpResponse('xContact')
            return HttpResponse('xExist')
        except:
            return HttpResponse('xEverything')

    get_this = Health_center_contactInformation.objects.select_related(
        None).all()[:1]
    return JsonResponse([get_this.serialize() for get_this in get_this], safe=False)


@user_passes_test(admin_only, login_url='/')
def create_this_information(request):
    if request.method == "POST":
        add_opentime = request.POST.get('add_opentime')
        add_closingtime = request.POST.get('add_closingtime')
        add_contactnum = request.POST.get('add_contactnum')

        try:
            add_contactnum = int(add_contactnum)
            if add_closingtime <= add_opentime:
                return HttpResponse('xTime')
            if verify_doctor_contactnum(request, add_contactnum):

                # Int to string
                add_contactnum = str(add_contactnum)

                # Declare an empty list
                this_list = []

                # Declare an empty string
                this_contact_num = ""

                # Append each string to a list(list of strings)
                for each_str in add_contactnum:
                    this_list.append(each_str)

                this_list.insert(0, '6')
                this_list.insert(1, '3')

                # list to str
                for obj in this_list:
                    this_contact_num += obj

                Health_center_contactInformation.objects.create(
                    Name=request.POST.get('add_name'),
                    Address=request.POST.get('add_address'),
                    Contact_number=this_contact_num,
                    Email_address=request.POST.get('add_email'),
                    Available_days=request.POST.get('add_days'),
                    Open_time=request.POST.get('add_opentime'),
                    Close_time=request.POST.get('add_closingtime'),
                    Open_today=request.POST.get('add_status_today'),
                )
                return HttpResponse('')
            return HttpResponse('xContact')
        except:
            return HttpResponse('xEverything')
    return None


@user_passes_test(admin_only, login_url='/')
def donation_page(request):

    context = {
        "title": "Donation",
        "segment": "Donation"
    }

    return render(request, 'Health_services/admin_side/Donation.html', context)


@user_passes_test(admin_only, login_url='/')
def create_this_donation(request):
    if request.method == "POST":
        Bank_image = request.FILES.get('Bank_image', False)

        a, is_created = Donation_info.objects.get_or_create(
            Bank=request.POST.get('Bank_name'),
            Account_name=request.POST.get('Account_name'),
            Account_number=request.POST.get('Account_number'),
        )

        if is_created is True:
            if Bank_image is not False:
                get_this_new_info = Donation_info.objects.get(
                    Bank=request.POST.get('Bank_name'),
                    Account_name=request.POST.get('Account_name'),
                    Account_number=request.POST.get('Account_number'),
                )
                get_this_new_info.Bank_image = request.FILES['Bank_image']
                get_this_new_info.save()
                return HttpResponse('Add')
            return HttpResponse('Add')
        return HttpResponse('xInfo')
    return None


@user_passes_test(admin_only, login_url='/')
def update_this_donation(request):
    if request.method == "POST":
        Bank_image = request.FILES.get('upd_Bank_image', False)
        Bank_id = int(request.POST.get('upd_Bank_id'))

        if Donation_info.objects.filter(id=Bank_id).exists():
            Donation_info.objects.filter(id=Bank_id).update(
                Bank=request.POST.get('upd_Bank_name'),
                Account_name=request.POST.get('upd_Account_name'),
                Account_number=request.POST.get('upd_Account_number'),
            )
            if Bank_image is not False:
                update_this = Donation_info.objects.get(id=Bank_id)
                update_this.Bank_image = request.FILES['upd_Bank_image']
                update_this.save()
            return HttpResponse('Updated Successfully.')
        return HttpResponse('xExists')
    return None


@user_passes_test(admin_only, login_url='/')
def delete_this_donation(request):
    if request.method == "POST":
        Bank_id = int(request.POST.get('del_Bank_id'))

        if Donation_info.objects.filter(id=Bank_id).exists():
            Donation_info.objects.filter(id=Bank_id).delete()
            return HttpResponse('Deleted Successfully.')
        return HttpResponse('xExist')
    return None


@user_passes_test(admin_only, login_url='/')
def get_this_donation_info(request, pk):
    if Donation_info.objects.filter(id=pk).exists():
        this_info = Donation_info.objects.filter(id=pk).select_related(None)
        return JsonResponse([this_info.serialize() for this_info in this_info], safe=False)
    return HttpResponse('xExist')


@user_passes_test(admin_only, login_url='/')
def get_list_of_donations(request):
    this_data = Donation_info.objects.select_related(
        None).order_by(Lower('Bank'))
    return JsonResponse([this_data.serialize() for this_data in this_data], safe=False)


@user_passes_test(admin_only, login_url='/')
def Doctor_specialization_page(request):

    context = {
        "title": "Doctor Specialization",
        "segment": "Doctor Specialization"
    }
    return render(request, 'Health_services/admin_side/Doctors_specialization.html', context)


@user_passes_test(admin_only, login_url='/')
def get_all_Doctor_specialization(request):
    get_this = Doctors_specialty.objects.select_related(
        None).filter(Is_visible=True).order_by(Lower('Title'))
    return JsonResponse([get_this.serialize() for get_this in get_this], safe=False)


@user_passes_test(admin_only, login_url='/')
def Create_this_Doctor_specialization(request):
    if request.method == "POST":
        Title = request.POST.get('add_Title')
        if Doctors_specialty.objects.filter(Title__iexact=Title, Is_visible=True):
            return HttpResponse('xTitle')
        elif Doctors_specialty.objects.filter(Title__iexact=Title, Is_visible=False):
            Doctors_specialty.objects.filter(Title__iexact=Title).update(
                Title=request.POST.get('add_Title'),
                Description=request.POST.get('add_Description'),
                Is_visible=True
            )
            return HttpResponse('Added')
        else:
            Doctors_specialty.objects.create(
                Title=request.POST.get('add_Title'),
                Description=request.POST.get('add_Description'),
                Is_visible=True
            )
            return HttpResponse('Added')
    return None


@user_passes_test(admin_only, login_url='/')
def Update_this_Doctor_specialization(request):
    if request.method == "POST":
        Update_this_id = int(request.POST.get('upd_id'))
        Update_this_name = request.POST.get('upd_Title')
        if Doctors_specialty.objects.filter(id=Update_this_id, Is_visible=True):
            if Doctors_specialty.objects.filter(Title__iexact=Update_this_name).exclude(id=Update_this_id).exists():
                return HttpResponse('xName')
            Doctors_specialty.objects.filter(id=Update_this_id).update(
                Title=request.POST.get('upd_Title'),
                Description=request.POST.get('upd_Description'),
            )
            return HttpResponse('Updated')
        return HttpResponse('xExist')
    return None


@user_passes_test(admin_only, login_url='/')
def Delete_this_Doctor_specialization(request):
    if request.method == "POST":
        Delete_this_id = int(request.POST.get('del_id'))
        if Doctors_specialty.objects.filter(id=Delete_this_id, Is_visible=True).exists():
            Doctors_specialty.objects.filter(id=Delete_this_id).update(
                Is_visible=False
            )
            return HttpResponse('Deleted')
        return HttpResponse('xExist')
    return None


@user_passes_test(admin_only, login_url='/')
def get_this_Doctor_specialization_info(request, pk):
    if Doctors_specialty.objects.filter(id=pk, Is_visible=True).exists():
        send_this = Doctors_specialty.objects.select_related(
            None).filter(id=pk)
        return JsonResponse([send_this.serialize() for send_this in send_this], safe=False)
    return HttpResponse('xExist')


@user_passes_test(admin_only, login_url='/')
def verification_page(request):

    context = {

        "title": "Verification Requests",
        "segment": "Verification Requests"
    }
    return render(request, 'Health_services/admin_side/Verification_requests.html', context)


@user_passes_test(admin_only, login_url='/')
def get_lists_verification_requests(request):
    this_lists = Health_service_recipients.objects.select_related(
        None).exclude(Is_verified=True)
    return JsonResponse([this_lists.serialize() for this_lists in this_lists], safe=False)


@user_passes_test(admin_only, login_url='/')
def accept_this_verification_request(request):
    if request.method == "POST":
        this_id = int(request.POST.get('accept_this_id'))
        if Health_service_recipients.objects.filter(id=this_id, Is_verified=False).exists():
            Health_service_recipients.objects.filter(id=this_id).update(
                Is_verified=True)
            return HttpResponse('accepted')
        return HttpResponse('xExists')
    return None


@user_passes_test(admin_only, login_url='/')
def decline_this_verification_request(request):
    if request.method == "POST":
        this_id = int(request.POST.get('dis_accept_this_id'))
        if Health_service_recipients.objects.filter(id=this_id, Is_verified=False).exists():
            Health_service_recipients.objects.filter(id=this_id).delete()
            return HttpResponse('denied')
        return HttpResponse('xExists')
    return None


@user_passes_test(admin_only, login_url='/')
def get_verification_info(request, pk):
    if Health_service_recipients.objects.filter(id=pk, Is_verified=False).exists():
        send_this = Health_service_recipients.objects.select_related(
            None).filter(id=pk)
        return JsonResponse([send_this.serialize() for send_this in send_this], safe=False)
    return HttpResponse('xExists')


# ---------- CLIENT SIDE ----------------------------------------------------------------------------


@user_passes_test(check_user_type_clientSide, login_url='supersystem_webpages-superuser')
def index(request):

    get_status = None

    if Health_center_contactInformation.objects.filter(Open_today=True).exists():
        get_status = Health_center_contactInformation.objects.select_related(
            None).filter(Open_today=True).first()

    get_seasonal_service = Seasonal_health_service.objects.filter(
        Start_date__lte=datetime.date.today(),
        End_date__gte=datetime.date.today(),
        Is_deleted=False
    )

    get_contact_information = Health_center_contactInformation.objects.values(
        'Name',
        'Address',
        'Contact_number',
        'Email_address'
    ).first()

    get_donation_infos = Donation_info.objects.select_related(None)

    context = {
        'navbar_user': user_image_name(request),
        'year': datetime.datetime.now(),
        'health_center_is_open': get_status,
        'get_seasonal_service': get_seasonal_service,
        'get_contact_information': get_contact_information,
        'get_donation_infos': get_donation_infos,
    }
    return render(request, 'Health_services/client_side/index.html', context)


@user_passes_test(check_user_type_clientSide, login_url='supersystem_webpages-superuser')
def index_available_health_services(request):
    context = {
        'navbar_user': user_image_name(request),
        'title': 'Seasonal Services',
    }
    return render(request, 'Health_services/client_side/Health_services_page.html', context)


@user_passes_test(check_user_type_clientSide, login_url='supersystem_webpages-superuser')
def get_available_health_services(request):

    list_of_ongoing_services = Seasonal_health_service.objects.filter(
        Start_date__lte=datetime.date.today(),
        End_date__gte=datetime.date.today()
    ).exclude(
        Q(Is_deleted=True) | Q(End_date=datetime.date.today(),
                               Close_time__lte=datetime.datetime.now())
    ).order_by('id')

    count_participant = Seasonal_health_service.objects.values('Title').filter(
        Start_date__lte=datetime.date.today(),
        End_date__gte=datetime.date.today(),
    ).exclude(
        Q(Is_deleted=True) | Q(End_date=datetime.date.today(),
                               Close_time__lte=datetime.datetime.now())
    ).annotate(
        entries=Count('Service_type', filter=Q(
            Service_type__Is_cancelled=False))
    ).order_by('id')

    context = {
        'services': [list_of_ongoing_services.serialize() for list_of_ongoing_services in list_of_ongoing_services],
        'participant': list(count_participant)
    }

    return JsonResponse(context, safe=False)


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def set_appointment_for_this_seasonal_service(request, pk):
    if Seasonal_health_service.objects.filter(id=pk, Is_deleted=False).exists():
        this_service = Seasonal_health_service.objects.get(id=pk)
        if this_service.Start_date <= datetime.date.today() and this_service.End_date >= datetime.date.today():
            if Health_service_recipients.objects.filter(User_account__id=request.user.id, Is_verified=True).exists():
                if SeasonalServices_request.objects.filter(Name__id=request.user.id, Service_type__id=pk, Is_cancelled=False).exists():
                    user_existing_appointment_service = SeasonalServices_request.objects.filter(
                        Name__id=request.user.id, Service_type__id=pk).exclude(Is_cancelled=True)

                    for obj in user_existing_appointment_service:
                        if obj.Appointment_date >= datetime.date.today():
                            return HttpResponse('xNewAppointment')

                    # Add another appointment
                    return HttpResponse('addNew')

                # Create new appointment
                return HttpResponse('newCreate')
            return HttpResponse('xVerified')
        return HttpResponse('expired')
    return HttpResponse('xExist')


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def return_this_health_service_info(request, pk):
    if Seasonal_health_service.objects.filter(id=pk, Is_deleted=False).exists():
        get_info = Seasonal_health_service.objects.select_related(
            None).filter(id=pk)
        return JsonResponse([get_info.serialize() for get_info in get_info], safe=False)
    return HttpResponse('The service no longer exist.')


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def create_this_health_appointment_request(request):
    if request.method == "POST":
        Applicant_name = request.POST.get('Applicant_name')
        Appointment_date = datetime.datetime.strptime(
            request.POST.get('Appointment_date'), "%Y-%m-%d").date()

        try:
            Service_type_id = int(request.POST.get('Service_type_id'))
            if Seasonal_health_service.objects.filter(id=Service_type_id, Is_deleted=False).exists():
                if Applicant_name or Appointment_date is not None:
                    if Appointment_date >= datetime.date.today():
                        get_this_date = Seasonal_health_service.objects.get(
                            id=Service_type_id)
                        if Appointment_date > get_this_date.End_date:
                            return HttpResponse('endDate')

                        if Appointment_date == datetime.date.today() and datetime.datetime.now().time() >= get_this_date.Close_time:
                            return HttpResponse('xTime')

                        SeasonalServices_request.objects.create(
                            Name=User.objects.get(id=request.user.id),
                            Beneficiary_name=Applicant_name,
                            Service_type=Seasonal_health_service.objects.get(
                                id=Service_type_id),
                            Appointment_date=request.POST.get(
                                'Appointment_date'),
                        )
                        return HttpResponse('Added')
                    return HttpResponse('xDate')
                return HttpResponse('xFields')
            return HttpResponse('xExist')
        except:
            return HttpResponse('Something wrong')
    return None


@user_passes_test(check_user_type_clientSide, login_url='supersystem_webpages-superuser')
def health_service_get_freecheckup_assigned_doctors(request):
    send_this_list = Check_up.objects.filter(Is_available=True)
    return JsonResponse([send_this_list.serialize() for send_this_list in send_this_list], safe=False)


@user_passes_test(check_user_type_clientSide, login_url='supersystem_webpages-superuser')
def index_get_list_of_Labtests(request):
    send_this = Laboratory_test.objects.filter(Is_available=True)
    return JsonResponse([send_this.serialize() for send_this in send_this], safe=False)


@user_passes_test(check_user_type_clientSide, login_url='supersystem_webpages-superuser')
def Doctor_profile_and_credentials(request, pk):
    get_doctor_profile = Doctor.objects.select_related(
        None).filter(id=pk, Still_active=True).first()
    get_doctor_credentials = Doctors_credential.objects.select_related(None).filter(
        Doctor_name__id=pk, Is_visible=True)

    context = {
        'navbar_user': user_image_name(request),
        'title': 'Doctor Profile',
        'Doctor_profile': get_doctor_profile,
        'Doctor_credentials': get_doctor_credentials,
    }
    return render(request, 'Health_services/client_side/Doctor_fulldetails.html', context)


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def Appointment_history(request):

    context = {
        'navbar_user': user_image_name(request),
        'title': 'Appointment History',
    }
    return render(request, 'Health_services/client_side/Appointment_history.html', context)


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def get_list_of_ongoing_appointments(request):
    ss_ongoing_appointment = SeasonalServices_request.objects.filter(
        Name__id=request.user.id, Appointment_date__gte=datetime.date.today()
    ).exclude(Is_cancelled=True).order_by('-Appointment_date')

    labtest_ongoing_appointment = LabTest_request.objects.filter(
        Name__id=request.user.id, Appointment_date__gte=datetime.date.today()
    ).exclude(Is_cancelled=True)

    context = {
        'ss_ongoing_appointment': [ss_ongoing_appointment.serialize() for ss_ongoing_appointment in ss_ongoing_appointment],
        'labtest_ongoing_appointment': [labtest_ongoing_appointment.serialize() for labtest_ongoing_appointment in labtest_ongoing_appointment],
    }

    return JsonResponse(context, safe=False)


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def get_list_of_previous_appointment(request):
    ss_previous_appointment = SeasonalServices_request.objects.filter(
        Name__id=request.user.id, Appointment_date__lt=datetime.date.today()
    ).exclude(Is_cancelled=True).order_by('-Appointment_date')

    labtest_previous_appointment = LabTest_request.objects.filter(
        Name__id=request.user.id, Appointment_date__lt=datetime.date.today()
    ).exclude(Is_cancelled=True)

    context = {
        'ss_previous_appointment': [ss_previous_appointment.serialize() for ss_previous_appointment in ss_previous_appointment],
        'labtest_previous_appointment': [labtest_previous_appointment.serialize() for labtest_previous_appointment in labtest_previous_appointment],
    }
    return JsonResponse(context, safe=False)


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def get_list_of_cancelled_appointments(request):
    ss_cancelled_appointment = SeasonalServices_request.objects.filter(
        Name__id=request.user.id, Is_cancelled=True
    ).order_by('-modified')

    labtest_cancelled_appointment = LabTest_request.objects.filter(
        Name__id=request.user.id, Is_cancelled=True
    ).order_by('-modified')

    context = {
        'ss_cancelled_appointment': [ss_cancelled_appointment.serialize() for ss_cancelled_appointment in ss_cancelled_appointment],
        'labtest_cancelled_appointment': [labtest_cancelled_appointment.serialize() for labtest_cancelled_appointment in labtest_cancelled_appointment],
    }

    return JsonResponse(context, safe=False)


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def get_this_health_appointment_info(request, pk):
    if SeasonalServices_request.objects.filter(id=pk, Is_cancelled=False, Appointment_date__gte=datetime.date.today()).exists():
        send_this_info = SeasonalServices_request.objects.filter(id=pk)
        return JsonResponse([send_this_info.serialize() for send_this_info in send_this_info], safe=False)
    return HttpResponse('xExist')


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def cancel_this_health_appointment(request):
    if request.method == "POST":
        try:
            cancel_this_id = int(request.POST.get('cancel_this_id'))
            if SeasonalServices_request.objects.filter(id=cancel_this_id, Is_cancelled=False, Appointment_date__gte=datetime.date.today()).exists():
                SeasonalServices_request.objects.filter(
                    id=cancel_this_id).update(Is_cancelled=True)
                return HttpResponse('cancelled')
            return HttpResponse('xExist')
        except:
            return HttpResponse('Something is wrong')
    return None


@user_passes_test(user_account_only, login_url='supersystem_webpages-login')
def cancel_this_labtest_request(request):
    if request.method == "POST":
        try:
            cancel_this_id_labtest = int(
                request.POST.get('cancel_this_id_labtest'))
            cancel_this_appt = LabTest_request.objects.get(
                id=cancel_this_id_labtest)

            if cancel_this_appt is not None:
                if cancel_this_appt.Is_cancelled == False:
                    if cancel_this_appt.Appointment_date >= datetime.date.today():
                        LabTest_request.objects.filter(id=cancel_this_id_labtest).update(
                            Is_cancelled=True
                        )
                        return HttpResponse('success')
                    return HttpResponse('expired')
                return HttpResponse('xCancelled')
            return HttpResponse('xExist')

        except:
            return HttpResponse('Something is wrong')

    return None


def user_is_not_validated(user):
    if user.is_authenticated:
        if not user.is_superuser:
            if Health_service_recipients.objects.filter(User_account__id=user.id, Is_verified=True).exists():
                return False
            return True
        return False
    return False


@user_passes_test(user_is_not_validated, login_url='supersystem_webpages-login')
def validate_user_page(request):

    send_this_data = Health_service_recipients.objects.select_related('User_account').filter(
        User_account__id=request.user.id, Is_verified=False).first()

    context = {
        'navbar_user': user_image_name(request),
        'title': 'Validate Health Recipient',
        'send_this_data': send_this_data,
    }
    return render(request, 'Health_services/client_side/User_validation.html', context)


@user_passes_test(user_is_not_validated, login_url='supersystem_webpages-login')
def validate_this_document(request):
    if request.method == "POST":
        validate_this_pic = request.FILES.get('validate_this_pic', False)

        try:
            if Health_service_recipients.objects.filter(User_account__id=request.user.id, Is_verified=False).exists():
                return HttpResponse('waiting')
            elif Health_service_recipients.objects.filter(User_account__id=request.user.id, Is_verified=True).exists():
                return HttpResponse('accepted')
            else:
                if validate_this_pic is not False:
                    Health_service_recipients.objects.create(
                        User_account=User.objects.get(id=request.user.id),
                        User_document=validate_this_pic,
                        Is_verified=False
                    )
                    return HttpResponse('pending')
                return HttpResponse('No Image')

        except:
            return HttpResponse('Something is wrong')
    return None


@user_passes_test(user_is_not_validated, login_url='supersystem_webpages-login')
def cancel_this_application(request):
    if request.method == "POST":
        try:
            cancel_this_id = int(request.POST.get('cancel_this_id'))
            if Health_service_recipients.objects.filter(id=cancel_this_id, Is_verified=True).exists():
                return HttpResponse('accepted')

            elif Health_service_recipients.objects.filter(id=cancel_this_id, Is_verified=False).exists():
                Health_service_recipients.objects.filter(
                    id=cancel_this_id).delete()
                return HttpResponse('deleted')

            else:
                return HttpResponse('xExist')

        except:
            return HttpResponse('Something is wrong')

    return None


@user_passes_test(user_account_only, login_url='supersystem_webpages-superuser')
def verify_in_lab_test(request, pk):
    if Laboratory_test.objects.filter(id=pk, Is_available=True).exists():
        if Laboratory_test.objects.filter(id=pk, Need_appointment=True).exists():
            if LabTest_request.objects.filter(
                Name__id=request.user.id,
                Requested_labTest__id=pk,
                Appointment_date__gte=datetime.date.today()
            ).exclude(Is_cancelled=True).exists():
                return HttpResponse('xNewAppointment')

            if Laboratory_test.objects.filter(id=pk, Fees__gt=0).exists():
                return HttpResponse('continue')

            if Health_service_recipients.objects.filter(User_account__id=request.user.id, Is_verified=True).exists():
                return HttpResponse('continue')
            return HttpResponse('xVerified')

        return HttpResponse('xAppointment')
    return HttpResponse('xLab')


@user_passes_test(user_account_only, login_url='supersystem_webpages-superuser')
def get_labtest_request_information(request, pk):
    send_this = LabTest_request.objects.filter(id=pk, Is_cancelled=False)
    if send_this is not None:
        return JsonResponse([send_this.serialize() for send_this in send_this], safe=False)

    return HttpResponse('xExist')


@user_passes_test(user_account_only, login_url='supersystem_webpages-superuser')
def get_labtest_information(request, pk):
    get_this = Laboratory_test.objects.filter(id=pk)
    return JsonResponse([get_this.serialize() for get_this in get_this], safe=False)


@user_passes_test(user_account_only, login_url='supersystem_webpages-superuser')
def create_labtest_appointment_byClient(request):
    if request.method == "POST":
        try:
            Appointment_date = datetime.datetime.strptime(
                request.POST.get('Appointment_date'), "%Y-%m-%d").date()
            labtest_id = int(request.POST.get('labtest_id'))
            Beneficiary_name = request.POST.get('Beneficiary_name')

            verify_this_id = Laboratory_test.objects.get(
                id=labtest_id, Is_available=True)

            this_contact = Health_center_contactInformation.objects.select_related(
                None).first()

            if verify_this_id is not None:

                # Check for ongoing labtest with same id and appointment date is greater than or equal to date today
                if LabTest_request.objects.filter(
                    Name__id=request.user.id,
                    Requested_labTest__id=labtest_id,
                    Appointment_date__gte=datetime.date.today()
                ).exclude(Is_cancelled=True).exists():
                    return HttpResponse('DuplicateAppointment')

                if verify_this_id.Need_appointment == True:
                    if Appointment_date >= datetime.date.today():

                        # Insert code here to validate date today appointment

                        if this_contact is not None:
                            if Appointment_date == datetime.date.today() and this_contact.Open_today == False:
                                return HttpResponse('hClose')

                            if Appointment_date == datetime.date.today() and datetime.datetime.now().time() >= this_contact.Close_time:
                                return HttpResponse('xTime')

                            if verify_this_id.Fees > 0:
                                LabTest_request.objects.create(
                                    Name=User.objects.get(id=request.user.id),
                                    Beneficiary_name=Beneficiary_name,
                                    Appointment_date=request.POST.get(
                                        'Appointment_date'),
                                    Requested_labTest=Laboratory_test.objects.get(
                                        id=labtest_id),
                                )
                                return HttpResponse('created')

                            if Health_service_recipients.objects.filter(User_account__id=request.user.id, Is_verified=True).exists():
                                LabTest_request.objects.create(
                                    Name=User.objects.get(id=request.user.id),
                                    Beneficiary_name=Beneficiary_name,
                                    Appointment_date=request.POST.get(
                                        'Appointment_date'),
                                    Requested_labTest=Laboratory_test.objects.get(
                                        id=labtest_id),
                                )
                                return HttpResponse('created')
                            return HttpResponse('xVerified')

                        return HttpResponse('The health center has no contact information.')

                    return HttpResponse('xDateAppointment')
                return HttpResponse('xAppointment')
            return HttpResponse('xExist')

        except:
            return HttpResponse('Something is wrong.')
    return None
