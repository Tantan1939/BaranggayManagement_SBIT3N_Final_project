"""BaranggayManagement_SBIT3N URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Import this to retrieve image path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Supersystem_webpages.urls')),
    path('Brgy_document_issuance/', include('Brgy_document_issuance.urls')),
    path('Brgy_report_generation/', include('Brgy_report_generation.urls')),
    path('Record_management/', include('Record_management.urls')),
    path('Health_services/', include('Health_services.urls')),
    path('Appointment_system/', include('Appointment_system.urls')),
]

# It is required to retrieve image path from this project
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
