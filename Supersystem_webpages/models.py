from email.policy import default
from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import RegexValidator

# Create your models here.


class Account_details(models.Model):
    Account_name = models.OneToOneField(User, on_delete=models.CASCADE)
    Age = models.PositiveIntegerField(null=True)
    Phone_numberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    Contact_number = models.CharField(
        validators=[Phone_numberRegex], max_length=13, unique=True, null=True)
    #Address = models.OneToOneField(Account_address, on_delete=models.CASCADE)
    Profile_picture = models.ImageField(
        default='default_profile.jpg', upload_to='Account_profile_images')
    Updated = models.DateTimeField(auto_now=True)
    Created = models.DateTimeField(auto_now_add=True)


class List_of_questions(models.Model):
    question = models.TextField()
    answer = models.TextField()
    Updated = models.DateTimeField(auto_now=True)
    Created = models.DateTimeField(auto_now_add=True)


class Brgy_photos(models.Model):
    description = models.CharField(max_length=50)
    picture = models.ImageField(upload_to="Brgy_images")
    Updated = models.DateTimeField(auto_now=True)
    Created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
