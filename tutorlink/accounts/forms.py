from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, TutorProfile, Child

SIGNUP_ROLE_CHOICES = [
    ('PARENT', 'Parent'),
    ('TUTOR', 'Tutor'),
]
# Django built-in UserCreationForm that gives 2 password boxes and matching check and hashing, we extend it and add our fields
# like roles
class SignupForm(UserCreationForm):
    role = forms.ChoiceField(choices=SIGNUP_ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'role', 'first_name', 'last_name')

    def clean_email(self):
        return self.cleaned_data.get('email').strip().lower()

# We extend the built-in AuthenticationForm to use email instead of username for login
class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

    def clean_username(self):
        return self.cleaned_data.get('username').strip().lower()

class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ['bio', 'qualification', 'years_experience', 'teaching_mode']


class ChildProfileForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name', 'level']

# General form for all users
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'address', 'date_of_birth', 'gender']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
