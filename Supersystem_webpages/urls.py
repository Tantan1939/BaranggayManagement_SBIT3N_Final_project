from unicodedata import name
from xml.etree.ElementInclude import include
from django.urls import path, include, re_path
from . import views

urlpatterns = [

    # CLIENT urls
    path('', views.index, name='supersystem_webpages-index'),
    path('login/', views.login_page, name='supersystem_webpages-login'),
    path('logout/', views.logout_btn, name='supersystem_webpages-logout'),
    path('create_account/', views.register_account_anyone,
         name='supersystem_webpages-createaccount'),

    path('update_account_details/', include([
        path('', views.update_account_details,
             name='supersystem_webpages-update'),
        path('func_update_profile_image/', views.func_update_profile_image,
             name='supersystem_webpages-profile-image'),
        path('func_get_account_details/', views.func_get_account_details,
             name='supersystem_webpages-func_get_account_details'),
        path('func_update_account_details/', views.func_update_account_details,
             name='supersystem_webpages-func_update_account_details'),
    ])),

    # ADMIN urls
    path('superuser/', include([
        path('', views.admin_index, name='supersystem_webpages-superuser'),
        path('list_of_residents/', views.view_residents,
             name='supersystem_webpages-superuser-list_of_residents'),
    ])),
]
