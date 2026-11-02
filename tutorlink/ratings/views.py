from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from enrolments.models import Package
from .forms import RatingForm, DisputeForm
from .models import Rating, Dispute
from django.db.models import Avg
from django.core.paginator import Paginator

# Create your views here.

@login_required
def rate_package_view(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    tutor = package.enrolment_request.listing.tutor
    parent = package.enrolment_request.child.parent

    # Build the rating with everything except the stars
    rating = Rating(rater=request.user, package=package)
    if request.user == parent:
        rating.rated_tutor = tutor
        target = tutor.user
    elif request.user == tutor.user:
        rating.rated_parent = parent
        target = parent
    else:
        return redirect('index')

    if Rating.objects.filter(rater=request.user, package=package).exists():
        messages.error(request, 'You have already rated this package')
        return redirect('my_ratings')

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your rating!')
            return redirect('my_ratings')
    else:
        form = RatingForm(instance=rating)

    return render(request, 'ratings/rate.html', {'form': form, 'package': package, 'target': target})


@login_required
def my_ratings_view(request):
    if request.user.role == 'TUTOR':
        received = Rating.objects.filter(rated_tutor__user=request.user)
        my_packages = Package.objects.filter(enrolment_request__listing__tutor__user=request.user)
    elif request.user.role == 'PARENT':
        received = Rating.objects.filter(rated_parent=request.user)
        my_packages = Package.objects.filter(enrolment_request__child__parent=request.user)
    else:
        return redirect('index')
    to_rate = my_packages.exclude(lessons__status='SCHEDULED').exclude(ratings__rater=request.user)
    given = Rating.objects.filter(rater=request.user).order_by('-created_at')
    received = received.order_by('-created_at')
    average = received.aggregate(Avg('stars'))['stars__avg']

    to_rate = to_rate.order_by("-id") 
    to_rate_page = Paginator(to_rate, 5).get_page(request.GET.get("to_rate_page"))
    received_page = Paginator(received, 10).get_page(request.GET.get("received_page"))
    given_page = Paginator(given, 10).get_page(request.GET.get("given_page"))
    
    return render(request,
                  'ratings/my_ratings.html',
                  {'average': average,
                   'to_rate_page': to_rate_page,
                   'received_page': received_page,
                   'given_page': given_page})

@login_required
def dispute_rating_view(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)

    # only the person who was rated can dispute it
    rated_user = rating.rated_tutor.user if rating.rated_tutor else rating.rated_parent
    if request.user != rated_user:
        return redirect('index')

    if Dispute.objects.filter(rating=rating).exists():
        messages.error(request, 'This rating has already been disputed')
        return redirect('my_disputes')

    if request.method == 'POST':
        form = DisputeForm(request.POST)
        if form.is_valid():
            dispute = form.save(commit=False)
            dispute.rating = rating
            dispute.raised_by = request.user
            dispute.rating_summary = str(rating)
            dispute.save()
            messages.success(request, 'Your dispute has been sent to staff')
            return redirect('my_disputes')
    else:
        form = DisputeForm()

    return render(request, 'ratings/dispute_form.html', {'form': form, 'rating': rating})


@login_required
def my_disputes_view(request):
    disputes = Dispute.objects.filter(raised_by=request.user).order_by('-created_at')
    return render(request, 'ratings/my_disputes.html', {'disputes': disputes})
