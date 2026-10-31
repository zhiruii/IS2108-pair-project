from django.shortcuts import render, redirect, get_object_or_404
from .models import Listing
from accounts.models import TutorProfile, LEVEL_CHOICES
from .forms import ListingForm
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def parent_listings_view(request):
    if request.user.role != "PARENT":
        return redirect("index")
    
    # filtering logic
    listings = Listing.objects.filter(status="OPEN")

    subject = request.GET.get("subject")
    if subject:
        listings = listings.filter(subject=subject)

    level = request.GET.get("level")
    if level:
        listings = listings.filter(level=level)

    weekday = request.GET.get("weekday")
    if weekday:
        listings = listings.filter(weekday=weekday)
        
    mode = request.GET.get("mode")
    if mode:
        listings = listings.filter(mode=mode)
        
    max_rate = request.GET.get("max_rate")
    if max_rate:
        listings = listings.filter(rate_per_hour__lte=max_rate)

    return render(request, "listings/parent_view_listings.html", {"listings": listings, 
                                                                  'subject_choices': Listing.SUBJECT_CHOICES,
                                                                  'level_choices': LEVEL_CHOICES,
                                                                  'weekday_choices': Listing.WEEKDAY_CHOICES,
                                                                  'mode_choices': Listing.MODE_CHOICES,
                                                                  'selected': request.GET})


@login_required
def tutor_listings_view(request):
    if request.user.role != "TUTOR":
        return redirect("index")
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect("tutor_profile_create")

    listings = profile.listings.all().order_by("weekday", "start_time")

    # Filter by status from the URL, e.g. ?status=OPEN
    status = request.GET.get("status")
    if status in ("OPEN", "FILLED", "CLOSED", "RESERVED"):
        listings = listings.filter(status=status)

    return render(
        request,
        "listings/tutor_view_listings.html",
        {"listings": listings, "status": status},
    )


@login_required
def create_listing_view(request):
    if request.user.role != "TUTOR":
        return redirect("index")  # Redirects non-tutors to index
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect("tutor_profile_create")

    if request.method == "POST":
        form = ListingForm(request.POST, instance=Listing(tutor=profile))
        if form.is_valid():
            form.save()
            return redirect("tutor_listings_view")

    else:
        form = ListingForm()  # Create an empty form for GET

    # invalid POST correctly falls through to re-render with errors
    return render(request, "listings/create_listing.html", {"form": form})


@login_required
def edit_listing_view(request, pk):
    if request.user.role != "TUTOR":
        return redirect("index")
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect("tutor_profile_create")
    listing = get_object_or_404(Listing, pk=pk, tutor=profile)
    if request.method == "POST":
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return redirect("tutor_listings_view")
    else:
        form = ListingForm(instance=listing)

    return render(
        request, "listings/create_listing.html", {"form": form, "title": "Edit Listing"}
    )


@login_required
def close_listing_view(request, pk):
    if request.user.role != "TUTOR":
        return redirect("index")
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect("tutor_profile_create")
    listing = get_object_or_404(Listing, pk=pk, tutor=profile)
    if request.method == "POST":
        listing.status = "CLOSED"
        listing.save()
    return redirect("tutor_listings_view")
