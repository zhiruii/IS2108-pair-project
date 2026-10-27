from django.shortcuts import render, redirect, get_object_or_404
from .models import Listing
from accounts.models import TutorProfile
from .forms import ListingForm
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def parent_listings_view(request):
    if request.user.role != 'PARENT':
        return redirect('index')
    
    return render(request, 'listings/parent_view_listings.html', )

@login_required
def tutor_listings_view(request):
    if request.user.role != 'TUTOR':
        return redirect('index')
    
    return render(request, 'listings/tutor_view_listings.html', )

@login_required
def create_listing_view(request):
    if request.user.role != 'TUTOR':
        return redirect('index') # Redirects non-tutors to index
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect('tutor_profile_create')
    
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=Listing(tutor=profile))
        if form.is_valid():
            form.save()
            return redirect('tutor_listings_view')
        
    else: 
        form = ListingForm() # Create an empty form for GET
    
    # invalid POST correctly falls through to re-render with errors
    return render(request, 'listings/create_listing.html', {'form': form})

    
    
    
    