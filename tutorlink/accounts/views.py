from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm

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