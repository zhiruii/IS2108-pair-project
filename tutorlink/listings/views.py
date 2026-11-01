from django.shortcuts import render, redirect, get_object_or_404
from .models import Listing
from accounts.models import TutorProfile, LEVEL_CHOICES
from .forms import ListingForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from enrolments.utils import expire_overdue_requests
from django.core.paginator import Paginator

# Create your views here.
@login_required
def parent_listings_view(request):
    if request.user.role != "PARENT":
        return redirect("index")

    expire_overdue_requests()

    # filtering logic
    listings = Listing.objects.filter(status="OPEN").annotate(
        avg_rating=Avg("tutor__ratings_received__stars"),
        rating_count=Count("tutor__ratings_received"),
    ).order_by("weekday", "start_time")

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
        
    paginator = Paginator(listings, 10)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    params = request.GET.copy()     # copy of all the filters in the URL
    params.pop("page", None)        # take out the old page number
    querystring = params.urlencode()  # turn it back into text: "subject=MATH&mode=ONLINE"  

    return render(
        request,
        "listings/parent_view_listings.html",
        {
            "page_obj": page_obj,
            "subject_choices": Listing.SUBJECT_CHOICES,
            "level_choices": LEVEL_CHOICES,
            "weekday_choices": Listing.WEEKDAY_CHOICES,
            "mode_choices": Listing.MODE_CHOICES,
            "selected": request.GET,
            "querystring": querystring
        },
    )


@login_required
def tutor_listings_view(request):
    if request.user.role != "TUTOR":
        return redirect("index")
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect("tutor_profile_create")

    expire_overdue_requests()

    listings = (
        profile.listings.all()
        .annotate(
            pending_count=Count(
                "enrolment_requests",
                filter=Q(enrolment_requests__status="PENDING"),
            )
        )
        .order_by("weekday", "start_time")
    )

    # Filter by status from the URL, e.g. ?status=OPEN
    status = request.GET.get("status")
    if status in ("OPEN", "FILLED", "CLOSED", "RESERVED"):
        listings = listings.filter(status=status)
        
    paginator = Paginator(listings, 10)
    page_number = request.GET.get("page")
    listings_page = paginator.get_page(page_number)

    return render(
        request,
        "listings/tutor_view_listings.html",
        {"listings_page": listings_page, "status": status},
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


@login_required
def tutor_public_profile_view(request, pk):
    if request.user.role != "PARENT":
        return redirect("index")

    profile = get_object_or_404(TutorProfile, pk=pk)
    # 1. that tutor's OPEN listings, ordered by weekday and start_time
    listings = profile.listings.filter(status="OPEN").order_by("weekday", "start_time")
    # 2. rating summary: 
    ratings = profile.ratings_received.aggregate(avg=Avg("stars"), count=Count("id"))
    return render(request, 
                  "listings/tutor_public_profile.html",
                  {'profile': profile,
                   'listings': listings,
                   'ratings': ratings})