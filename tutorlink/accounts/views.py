from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .models import TutorProfile
from .forms import SignupForm, TutorProfileForm, EmailLoginForm

# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Bring the user tutor to the tutor profile creation page
            if user.role == 'TUTOR':
                return redirect('tutor_profile_create')
            # Bring user to index if parent
            return redirect('index')

    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # A tutor who didnt finish their profile goes back to finish it
            if user.role == 'TUTOR' and not TutorProfile.objects.filter(user=user).exists():
                return redirect('tutor_profile_create')
            return redirect('index')
    else:
        form = EmailLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('index')


# Need to be a user first to create a tutor profile, so we use the login_required decorator
@login_required
def tutor_profile_create_view(request):
    if request.user.role != 'TUTOR':
        return redirect('index')  # Redirect non-tutors to index
    if TutorProfile.objects.filter(user=request.user).exists():
        return redirect('index')  # Redirect if profile already exists

    if request.method == 'POST':
        form = TutorProfileForm(request.POST)
        if form.is_valid():
            # commit = False so we dont write into the database yet, we need to set the user first
            tutor_profile = form.save(commit=False)
            # Set the user of the tutor profile to the currently logged-in user
            tutor_profile.user = request.user
            tutor_profile.save()
            return redirect('index')  # Redirect to index after profile creation

    else:
        form = TutorProfileForm()
    return render(request, 'accounts/tutor_profile_create.html', {'form': form})