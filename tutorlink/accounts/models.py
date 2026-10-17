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
