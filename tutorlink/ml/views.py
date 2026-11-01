from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import TutorProfile
from .forms import PriceForm
from .predict import predict_ranges
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