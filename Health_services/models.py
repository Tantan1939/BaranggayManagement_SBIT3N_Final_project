from email.policy import default
from pickle import TRUE
from turtle import ondrag
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

# Create your models here.


def split_this_contactnum(cnum):
    # convert this int type into an str object
    cnum = str(cnum)

    # Initialize a list
    this_list = []

    # Iterate each str into list of str
    for obj in cnum:
        this_list.append(obj)

    # Remove 6 3 from the list
    this_list.pop(0)
    this_list.pop(0)

    # initialize new str variable
    new_doc_contact_num = ""

    # iterate each list item and append to str variable
    for each_lst in this_list:
        new_doc_contact_num += each_lst

    # convert str into int
    new_doc_contact_num = int(new_doc_contact_num)

    # return the update contact num to be display back to caller
    return new_doc_contact_num


class Doctors_specialty(models.Model):
    Title = models.CharField(max_length=50, unique=True)
    Description = models.TextField()
    Is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.Title

    def serialize(self):
        return{
            'id': self.id,
            'Title': self.Title,
            'Description': self.Description,
        }


class Doctor(models.Model):
    Name = models.CharField(max_length=50, unique=True)
    Age = models.PositiveIntegerField()
    Phone_numberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    Contact_number = models.CharField(
        validators=[Phone_numberRegex], max_length=12, null=True)
    Specialty = models.ForeignKey(
        Doctors_specialty, on_delete=models.CASCADE)
    Picture = models.ImageField(
        default='Default_doctor.png', upload_to='Health_services-Doctors_profile_images')
    Still_active = models.BooleanField(default=True)

    def __str__(self):
        return self.Name

    def serialize(self):
        return{
            "id": self.id,
            "Name": self.Name,
            "Age": self.Age,
            "Contact_number": self.Contact_number,
            "Specialty": self.Specialty.Title,
            "Specialty_id": self.Specialty.id,
            "Picture": self.Picture.url if self.Picture else None,
            "Still_active": self.Still_active
        }

    def edit_serialize(self):
        return{
            "id": self.id,
            "Name": self.Name,
            "Age": self.Age,
            "Contact_number": split_this_contactnum(self.Contact_number),
            "Specialty": self.Specialty.Title,
            "Specialty_id": self.Specialty.id,
            "Picture": self.Picture.url if self.Picture else None,
            "Still_active": self.Still_active
        }


class Doctors_credential(models.Model):
    Doctor_name = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    Title = models.CharField(max_length=50)
    Description = models.TextField()
    Awarded_date = models.DateField()
    Certificate_image = models.ImageField(
        upload_to='Health_services-Doctors_certificates')
    Is_visible = models.BooleanField(default=True)

    def __str__(self):
        return '%s, %s' % (self.Title, self.Doctor_name.Name)

    def serialize(self):
        return{
            "id": self.id,
            "Doctor_name": self.Doctor_name.Name,
            "Doctor_id": self.Doctor_name.id,
            "Title": self.Title,
            "Description": self.Description,
            "Awarded_date": self.Awarded_date,
            "Certificate_image": self.Certificate_image.url if self.Certificate_image else None,
        }


class Donation_info(models.Model):
    Bank = models.CharField(max_length=30)
    Bank_image = models.ImageField(
        upload_to='Health_services_Bank-images', default='Banking.jpg')
    Account_name = models.CharField(max_length=50)
    Account_number = models.CharField(max_length=50)

    def __str__(self):
        return self.Bank

    def serialize(self):
        return{
            'id': self.id,
            'Bank_name': self.Bank,
            'Bank_image': self.Bank_image.url,
            'Account_name': self.Account_name,
            'Account_number': self.Account_number,
        }


class Health_center_contactInformation(models.Model):
    Name = models.CharField(max_length=50)
    Address = models.CharField(max_length=100)
    Phone_numberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    Contact_number = models.CharField(
        validators=[Phone_numberRegex], max_length=12, unique=True)
    Email_address = models.EmailField()
    Available_days = models.CharField(max_length=20)
    Open_time = models.TimeField()
    Close_time = models.TimeField()
    Open_today = models.BooleanField(default=True)

    def __str__(self):
        return self.Name

    def serialize(self):
        return{
            "id": self.id,
            "Name": self.Name,
            "Address": self.Address,
            "Contact_number": split_this_contactnum(self.Contact_number),
            "Email_address": self.Email_address,
            "Available_days": self.Available_days,
            "Open_time": self.Open_time,
            "Close_time": self.Close_time,
            "Open_today": self.Open_today,
        }


class Check_up(models.Model):
    Assigned_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    Is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.Assigned_doctor.Name

    def serialize(self):
        return{
            'id': self.id,
            'Assigned_doctor_id': self.Assigned_doctor.id,
            'Assigned_doctor_Picture': self.Assigned_doctor.Picture.url,
            'Assigned_doctor_name': self.Assigned_doctor.Name,
            'Assigned_doctor_Specialty': self.Assigned_doctor.Specialty.Title,
            'Assigned_doctor_Specialty_description': self.Assigned_doctor.Specialty.Description,
        }


# seasonal health service
class Seasonal_health_service(models.Model):
    Assigned_doctor = models.ManyToManyField(Doctor)
    Title = models.CharField(max_length=50)
    Goal = models.TextField()
    Start_date = models.DateField()
    End_date = models.DateField()
    Open_time = models.TimeField()
    Close_time = models.TimeField()
    Location = models.CharField(max_length=60)
    Is_deleted = models.BooleanField(default=False)
    Image = models.ImageField(
        default='SS.png', upload_to="Health_services-Seasonal_services")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Title

    def serialize(self):
        return{
            "id": self.id,
            "Assigned_doctor_name": "%s" % (", ".join(Assigned_doctor.Name for Assigned_doctor in self.Assigned_doctor.all())),
            "Title": self.Title,
            "Goal": self.Goal,
            "Start_date": self.Start_date,
            "End_date": self.End_date,
            "Open_time": self.Open_time,
            "Close_time": self.Close_time,
            "Location": self.Location,
            "Image": self.Image.url,
        }


class Laboratory_test(models.Model):
    Title = models.CharField(max_length=50, unique=True)
    Description = models.TextField()
    Fees = models.PositiveBigIntegerField()
    Is_available = models.BooleanField(default=True)
    Need_appointment = models.BooleanField(default=True)

    def __str__(self):
        return self.Title

    def serialize(self):
        return{
            'id': self.id,
            'Title': self.Title,
            'Description': self.Description,
            'Fees': self.Fees,
            'Need_appointment': self.Need_appointment,
        }


class LabTest_request(models.Model):
    Name = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='Labtestrequest_name')
    Beneficiary_name = models.CharField(max_length=30)
    Requested_labTest = models.ForeignKey(
        Laboratory_test, on_delete=models.CASCADE, related_name='Requested_labTest')
    Appointment_date = models.DateField()
    Is_cancelled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s - %s' % (self.Name.username, self.Requested_labTest.Title)

    def serialize(self):
        return {
            'id': self.id,
            'owner_id': self.Name.id,
            'owner_name': self.Name.username,
            'Beneficiary_name': self.Beneficiary_name,
            'Requested_labTest_name': self.Requested_labTest.Title,
            'Requested_labTest_fees': self.Requested_labTest.Fees,
            'Appointment_date': self.Appointment_date,
            'Is_cancelled': self.Is_cancelled,
            'created': self.created,
            'modified': self.modified,
        }


class SeasonalServices_request(models.Model):
    Name = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='SSname')
    Beneficiary_name = models.CharField(max_length=40)
    Service_type = models.ForeignKey(
        Seasonal_health_service, on_delete=models.CASCADE, related_name='Service_type')
    Appointment_date = models.DateField()
    Is_cancelled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s - %s' % (self.Name.username, self.Service_type.Title)

    def serialize(self):
        return{
            'id': self.id,
            'user_id': self.Name.id,
            'user_username': self.Name.username,
            'Beneficiary_name': self.Beneficiary_name,
            'Service_type': self.Service_type.Title,
            'Service_image': self.Service_type.Image.url,
            'Appointment_date': self.Appointment_date,
            'created': self.created,
            'Is_cancelled': self.Is_cancelled,
            'modified': self.modified,
        }


class Health_service_recipients(models.Model):
    User_account = models.OneToOneField(User, on_delete=models.CASCADE)
    User_document = models.ImageField(
        upload_to='Health_services-User_documents')
    Application_date = models.DateField(auto_now_add=True)
    Last_modified_on = models.DateField(auto_now=True)
    Is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.User_account.username

    def serialize(self):
        return{
            'id': self.id,
            'user_username': self.User_account.username,
            'user_id': self.User_account.id,
            'User_document': self.User_document.url,
            'Application_date': self.Application_date,
            'Last_modified_on': self.Last_modified_on,
            'Is_verified': self.Is_verified,
        }
