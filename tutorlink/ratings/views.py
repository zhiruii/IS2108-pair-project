from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from enrolments.models import Package
from .forms import RatingForm
from .models import Rating
from django.db.models import Avg

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
            messages.success(request, 'Thank you for your rating')
            return redirect('my_ratings')
    else:
        form = RatingForm(instance=rating)

    return render(request, 'ratings/rate.html', {'form': form, 'package': package, 'target': target})


@login_required
def my_ratings_view(request):
    if request.user.role == 'TUTOR':
        received = Rating.objects.filter(rated_tutor__user=request.user)
    elif request.user.role == 'PARENT':
        received = Rating.objects.filter(rated_parent=request.user)
    else:
        return redirect('index')

    given = Rating.objects.filter(rater=request.user).order_by('-created_at')
    received = received.order_by('-created_at')
    average = received.aggregate(Avg('stars'))['stars__avg']

    return render(request, 'ratings/my_ratings.html', {'given': given, 'received': received, 'average': average})
