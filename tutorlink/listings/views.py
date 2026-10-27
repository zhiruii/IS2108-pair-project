from django.shortcuts import render, redirect, get_object_or_404
from .models import Listing
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def parent_listings_view(request):
    if request.user.role != 'PARENT':
        return redirect('index')
    
    return render(request, 'listings/parent_view_listings.html', )

def tutor_listings_view(request):
    if request.user.role != 'TUTOR':
        return redirect('index')
    
    return render(request, 'listings/tutor_view_listings.html', )