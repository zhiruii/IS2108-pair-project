from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import RestrictedError
from django.contrib import messages

from .models import TutorProfile, Child
from .forms import SignupForm, TutorProfileForm, EmailLoginForm, ChildProfileForm


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


@login_required
def child_list_view(request):
    # User must be parent to have children
    if request.user.role != 'PARENT':
        return redirect('index')

    children = Child.objects.filter(parent=request.user)
    return render(request, 'accounts/child_list.html', {'children': children})

@login_required
def child_create_view(request):
    # Create and edit will use same form
    if request.user.role != 'PARENT':
        return redirect('index')
    if request.method == 'POST':
        form = ChildProfileForm(request.POST)
        if form.is_valid():
            # Dont write into database first
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            return redirect('child_list')
    else:
        form = ChildProfileForm()
    return render(request, 'accounts/child_form.html', {'form': form})

@login_required
def child_edit_view(request, child_id):
    # Create and edit will use same child_form
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    if request.method == 'POST':
        form = ChildProfileForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            return redirect('child_list')
    else:
        form = ChildProfileForm(instance=child)
    return render(request, 'accounts/child_form.html', {'form': form})

@login_required
def child_delete_view(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    if request.method == 'POST':
        try:
            child.delete()
        except RestrictedError:
            # EnrolmentRequest in enrolments
            messages.error(request, 'This child has enrolment requests and cannot be deleted.')
        return redirect('child_list')
    return render(request, 'accounts/child_confirm_delete.html', {'child': child})