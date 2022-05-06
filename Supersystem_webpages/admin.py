from django.contrib import admin
from . models import Account_details, Brgy_photos, List_of_questions

# Register your models here.
admin.site.register(Account_details)
admin.site.register(List_of_questions)
admin.site.register(Brgy_photos)
