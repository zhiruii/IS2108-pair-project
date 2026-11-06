from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import TutorProfile
from .forms import PriceForm, FlagForm
from .predict import predict_ranges, ranges_for_listings, verdict, VERDICT_LABELS
from .models import PriceFlag
from django.contrib import messages
from django.db.models import Avg
from listings.models import Listing

FAR_OFF = 25
def size_of_gap(listing):
    return abs(listing.deviation or 0)


# Create your views here.
@login_required
def price_suggestion_view(request):
    if request.user.role != "TUTOR":
        return redirect("index")
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect("tutor_profile_create")

    suggestion = None
    form = PriceForm(request.POST or None)
    if form.is_valid():
        row = dict(form.cleaned_data)
        row["qualification"] = profile.qualification
        row["years_experience"] = profile.years_experience
        suggestion = predict_ranges([row])[0]
    return render(request, "ml/price_suggestion.html", {"form": form, "suggestion": suggestion})


@login_required
def price_review_view(request):
    if request.user.role != 'STAFF':
        return redirect('index')

    listings = Listing.objects.exclude(status='CLOSED').annotate(
        avg_rating=Avg('tutor__ratings_received__stars'),
    ).select_related('tutor__user', 'price_flag')

    status = request.GET.get('status', '')
    if status in ('OPEN', 'RESERVED', 'FILLED'):
        listings = listings.filter(status=status)

    listings = list(listings)
    ranges = ranges_for_listings(listings)
    for listing, price_range in zip(listings, ranges):
        listing.price_range = price_range
        listing.verdict = verdict(listing.rate_per_hour, price_range)
        listing.verdict_label = VERDICT_LABELS.get(listing.verdict)
        if price_range is None:
            listing.deviation = None
        else:
            # how far the rate is from the middle of the range, in percent
            mid = (price_range[0] + price_range[1]) / 2
            listing.deviation = round((float(listing.rate_per_hour) - mid) / mid * 100)

    dev = request.GET.get('dev', '')
    if dev == 'above':
        listings = [l for l in listings if l.deviation is not None and l.deviation >= FAR_OFF]
    elif dev == 'below':
        listings = [l for l in listings if l.deviation is not None and l.deviation <= -FAR_OFF]
    elif dev == 'out':
        listings = [l for l in listings if l.verdict in ('BELOW', 'ABOVE')]

    # biggest differences first
    listings.sort(key=size_of_gap, reverse=True)

    return render(request, 'ml/price_review.html',
                  {'listings': listings, 'status': status, 'dev': dev, 'far_off': FAR_OFF})


@login_required
def price_flag_view(request, listing_id):
    if request.user.role != 'STAFF':
        return redirect('index')

    listing = get_object_or_404(Listing, id=listing_id)

    if hasattr(listing, 'price_flag'):
        messages.error(request, 'This listing is already flagged')
        return redirect('price_review')

    if request.method == 'POST':
        form = FlagForm(request.POST)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.listing = listing
            flag.flagged_by = request.user
            flag.save()
            messages.success(request, 'Listing flagged')
            return redirect('price_review')
    else:
        form = FlagForm()

    return render(request, 'ml/price_flag.html', {'form': form, 'listing': listing})


@login_required
def price_unflag_view(request, listing_id):
    if request.user.role != 'STAFF':
        return redirect('index')

    flag = get_object_or_404(PriceFlag, listing_id=listing_id)
    if request.method == 'POST':
        flag.delete()
        messages.success(request, 'Flag cleared')
    return redirect('price_review')

@login_required
def price_flag_tutor_dismiss_view(request, listing_id):
    if request.user.role != 'TUTOR':
        return redirect('index')
    profile = TutorProfile.objects.filter(user=request.user).first()
    if profile is None:
        return redirect('tutor_profile_create')
    # only the tutor's own listing, so nobody can dismiss someone else's flag
    listing = get_object_or_404(Listing, pk=listing_id, tutor=profile)
    if request.method == 'POST':
        PriceFlag.objects.filter(listing=listing).delete()
    return redirect('tutor_listings_view')
