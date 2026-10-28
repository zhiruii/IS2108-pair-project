from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from listings.models import Listing
from accounts.models import Child
from .models import EnrolmentRequest
from .forms import EnrolmentRequestForm


# Create your views here.
@login_required
def send_enrolment_request_view(request, pk):
    if request.user.role != "PARENT":
        return redirect("index")
    listing = get_object_or_404(Listing, pk=pk, status="OPEN")
    children = Child.objects.filter(parent=request.user)
    if not children.exists():
        return redirect("child_create")

    if request.method == "POST":
        form = EnrolmentRequestForm(
            request.POST, instance=EnrolmentRequest(listing=listing), children=children
        )
        if form.is_valid():
            form.save()
            return redirect("parent_my_requests_view")

    else:
        form = EnrolmentRequestForm(children=children)

    return render(
        request,
        "enrolments/send_enrolment_request_view.html",
        {"form": form, "listing": listing},
    )


@login_required
def parent_my_requests_view(request):
    if request.user.role != "PARENT":
        return redirect("index")
    requests = EnrolmentRequest.objects.filter(child__parent=request.user).order_by(
        "-created_at"
    )
    return render(request, "enrolments/parent_my_requests_view.html", {'requests': requests})
