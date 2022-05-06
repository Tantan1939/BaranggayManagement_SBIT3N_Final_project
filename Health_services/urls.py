from unicodedata import name
from xml.etree.ElementInclude import include
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('', include([
         path('', views.index, name='Health_services-index'),

         path('Available_health_services/', include([
             path('', views.index_available_health_services,
              name='Health_services-Available_Health_service'),
             path('Get_available_health_services/',
                  views.get_available_health_services),
             path('Set_appointment_for_this_seasonal_service/<str:pk>',
                  views.set_appointment_for_this_seasonal_service),
             path('Return_this_health_service_info/<str:pk>',
                  views.return_this_health_service_info),
             path('Create_this_health_appointment_request/',
                  views.create_this_health_appointment_request),
         ])),

         path('Health_service_get_freecheckup_assigned_doctors/',
              views.health_service_get_freecheckup_assigned_doctors),
         path('Index_get_list_of_Labtests/', views.index_get_list_of_Labtests),
         path('Doctor_profile_and_credentials/<str:pk>',
              views.Doctor_profile_and_credentials),
         ])),

    path('Appointment_history/', include([
        path('', views.Appointment_history,
             name='Health_services-Appointment_history'),
        path('Get_list_of_ongoing_appointments/',
             views.get_list_of_ongoing_appointments),
        path('Get_list_of_previous_appointment/',
             views.get_list_of_previous_appointment),
        path('Get_list_of_cancelled_appointments/',
             views.get_list_of_cancelled_appointments),
        path('Get_this_health_appointment_info/<str:pk>',
             views.get_this_health_appointment_info),
        path('Cancel_this_health_appointment/',
             views.cancel_this_health_appointment),
    ])),

    path('Validation/', include([
         path('', views.validate_user_page, name='Health_services-Validation'),
         path('Validate_this_document/', views.validate_this_document),
         path('Cancel_this_application/', views.cancel_this_application),
         ])),

    path('Verify_in_lab_test/<str:pk>', include([
         path('', views.verify_in_lab_test),
         ])),

    path('Get_labtest_request_information/<str:pk>',
         views.get_labtest_request_information),
    path('Cancel_this_labtest_request/', views.cancel_this_labtest_request),
    path('Get_labtest_information/<str:pk>', views.get_labtest_information),
    path('Create_labtest_appointment_byClient/',
         views.create_labtest_appointment_byClient),


    # Admin URLS
    path('Health_services_superuser/', include([
        path('', views.admin_index, name='Health_services_superuser-index'),

        path('Laboratory_tests/', include([
            path('', views.Lab_test,
                 name='Health_services_superuser-Laboratory_tests'),
            path('Create_Laboratory_Test/', views.Create_Lab_Test),
            path('Get_Laboratory_Test/', views.get_Lab_test),
            path('Get_SingleLaboratory_test/<str:pk>', views.Get_single_labTest),
            path('Update_lab_test_info/', views.Update_lab_test_info),
            path('Del_lab_test_info/', views.Del_lab_test_info),
            path('generate_labtest_copies/', views.generate_labtest_copies,
                 name='Health_services_superuser-generate_labtest_copies'),
            path('Generate_seasonal_requests_copies/', views.generate_seasonal_requests_copies,
                 name='Health_services_superuser-Generate_seasonal_requests_copies'),
        ])),

        path('Doctors/', include([
            path('', views.list_of_doctors,
                 name='Health_services_superuser-Doctors'),
            path('get_list_of_doctors/', views.get_list_of_doctors),
            path('get_doctor_name_only/<str:pk>', views.get_doctor_name_only),
            path('Del_doctor/', views.Del_doctor),
            path('get_specialization/', views.get_specialization),
            path('get_all_specialization/', views.get_all_specialization),
            path('Create_doctor/', views.Create_doctor),
            path('get_single_doctor_info/<str:pk>',
                 views.get_single_doctor_info),
            path('update_doctor_info/', views.update_doctor_info),
            path('Credentials/<str:pk>', views.Doctors_credentials,
                 name='Health_services_superuser-Doctors_credentials'),
            path('Add_credentials/', views.Add_credentials),
            path('Get_credentials/', views.Get_credentials),
            path('get_single_credential/<str:pk>', views.get_single_credential),
            path('Delete_this_credential/', views.Delete_this_credential),
            path('Update_this_credential/', views.Update_this_credential),
        ])),

        path('Free_checkup/', include([
            path('', views.Free_checkup,
                 name='Health_services_superuser-Free_checkup'),
            path('Freecheckup_doctors/', views.get_freecheckup_doctors),
            path('Freecheckup_assign_doctor/', views.freecheckup_assign_doctor),
            path('Freecheckup_unassign_doctor/',
                 views.freecheckup_unassign_doctor),
        ])),

        path('Seasonal_services/', include([
             path('', views.Seasonal_health_Services,
                  name='Health_services_superuser-Seasonal_Services'),
             path('get_previous_health_services/',
                  views.get_previous_health_services),
             path('get_ongoing_health_services/',
                  views.get_ongoing_health_services),
             path('get_future_health_services/',
                  views.get_future_health_services),
             path('get_health_service_info/<str:pk>',
                  views.get_health_service_info),
             path('Delete_this_future_service/',
                  views.Delete_this_future_service),
             path('Delete_this_previous_service/',
                  views.Delete_this_previous_service),
             path('Add_this_service/', views.add_this_service),
             path('Update_this_service/', views.Update_this_service),
             ])),

        path('Health_center_informations/', include([
            path('', views.Health_center_informations,
                 name='Health_services_superuser-Health_center_informations'),
            path('Get_set_health_center_information/',
                 views.get_set_health_center_information),
            path('Create_this_information/', views.create_this_information),
        ])),

        path('Donation_info/', include([
             path('', views.donation_page,
                  name='Health_services_superuser-Donation_info'),
             path('Create_this_donation/', views.create_this_donation),
             path('Update_this_donation/', views.update_this_donation),
             path('Delete_this_donation/', views.delete_this_donation),
             path('Get_this_donation_info/<str:pk>',
                  views.get_this_donation_info),
             path('Get_list_of_donations/', views.get_list_of_donations),
             ])),

        path('Doctor_specialization/', include([
            path('', views.Doctor_specialization_page,
                 name='Health_services_superuser-Doctor_specialization'),
            path('Get_all_Doctor_specialization/',
                 views.get_all_Doctor_specialization),
            path('Create_this_Doctor_specialization/',
                 views.Create_this_Doctor_specialization),
            path('Update_this_Doctor_specialization/',
                 views.Update_this_Doctor_specialization),
            path('Delete_this_Doctor_specialization/',
                 views.Delete_this_Doctor_specialization),
            path('Get_this_Doctor_specialization_info/<str:pk>',
                 views.get_this_Doctor_specialization_info),
        ])),

        path('Verification_page/', include([
            path('', views.verification_page,
                 name='Health_services_superuser-verification_page'),
            path('Get_lists_verification_requests/',
                 views.get_lists_verification_requests),
            path('Accept_this_verification_request/',
                 views.accept_this_verification_request),
            path('Decline_this_verification_request/',
                 views.decline_this_verification_request),
            path('Get_verification_info/<str:pk>', views.get_verification_info),
        ])),
    ])),
]
