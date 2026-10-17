from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = [
    ('PARENT', 'Parent'),
    ('TUTOR', 'Tutor'),
    ('STAFF', 'Staff'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PARENT')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    # Mock payment only with last 4 digits
    card_brand = models.CharField(max_length=20, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)

    def save(self, *args, **kwargs):
        # Override AbstractUser save() to copy email into username
        self.email = self.email.strip().lower()
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


TEACHING_MODE_CHOICES = [
    ('IN_PERSON', 'In person'),
    ('ONLINE', 'Online'),
    ('HYBRID', 'Hybrid'),
]

QUALIFICATION_CHOICES = [
    ('STUDENT', 'Current university student'),
    ('DIPLOMA', 'Diploma'),
    ('DEGREE', 'Degree'),
    ('POSTGRAD', 'Masters or PhD'),
    ('NIE', 'NIE-trained / MOE teacher'),
    ('OTHER', 'Other'),
]

class TutorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500)
    qualification = models.CharField(max_length=40, choices=QUALIFICATION_CHOICES)
    years_experience = models.PositiveIntegerField(default=0)
    teaching_mode = models.CharField(max_length=10, choices=TEACHING_MODE_CHOICES)

LEVEL_CHOICES = [
    ('P1', 'Primary 1'),
    ('P2', 'Primary 2'),
    ('P3', 'Primary 3'),
    ('P4', 'Primary 4'),
    ('P5', 'Primary 5'),
    ('P6', 'Primary 6'),
    ('S1', 'Secondary 1'),
    ('S2', 'Secondary 2'),
    ('S3', 'Secondary 3'),
    ('S4', 'Secondary 4'),
    ('S5', 'Secondary 5'),
    ('JC1', 'JC 1'),
    ('JC2', 'JC 2'),
]

class Child(models.Model):
    parent = models.Model.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES)
