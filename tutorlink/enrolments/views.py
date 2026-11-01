from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from listings.models import Listing
from accounts.models import Child
from .models import EnrolmentRequest, Lesson
from .forms import EnrolmentRequestForm
from django.utils import timezone
from datetime import timedelta
from .utils import expire_overdue_requests

# Create your views here.
@login_required
def send_enrolment_request_view(request, pk):
    if request.user.role != "PARENT":
        return redirect("index")
    expire_overdue_requests()
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
    expire_overdue_requests()
    all_requests = EnrolmentRequest.objects.filter(child__parent=request.user).order_by(
        "-created_at"
    )
    active_status = ["ACCEPTED", "PENDING"]
    active_requests = all_requests.filter(status__in=active_status)
    past_requests = all_requests.exclude(status__in=active_status)
    return render(
        request, "enrolments/parent_my_requests_view.html", {"active_requests":active_requests, "past_requests":past_requests}
    )


@login_required
def parent_withdraw_request_view(request, pk):
    if request.user.role != "PARENT":
        return redirect("index")
    enrolment_request = get_object_or_404(
        EnrolmentRequest, pk=pk, status="PENDING", child__parent=request.user
    )

    if request.method == "POST":
        enrolment_request.status = "WITHDRAWN"
        reason = request.POST.get("withdraw_reason", "")
        enrolment_request.withdraw_reason = reason
        enrolment_request.save()
        return redirect("parent_my_requests_view")
    else:
        return render(request, "enrolments/parent_withdraw_request_view.html", {"enrolment_request": enrolment_request})
    
@login_required
def tutor_requests_view(request):
    if request.user.role != "TUTOR":
        return redirect("index")

    pending_requests = EnrolmentRequest.objects.filter(
        listing__tutor__user=request.user, status="PENDING"
    ).order_by("-created_at")

    # Only show one listing's requests when ?listing=<pk> is in the URL
    selected_listing = None
    listing_pk = request.GET.get("listing")
    if listing_pk:
        selected_listing = get_object_or_404(Listing, pk=listing_pk, tutor__user=request.user)
        pending_requests = pending_requests.filter(listing=selected_listing)

    return render(
        request,
        "enrolments/tutor_enrolment_requests_view.html",
        {"pending_requests": pending_requests, "selected_listing": selected_listing},
    )  

@login_required
def tutor_accept_request_view(request, pk):
    if request.user.role != "TUTOR":
        return redirect('index')
    enrolment_request = get_object_or_404(
        EnrolmentRequest, pk=pk, status="PENDING", listing__tutor__user=request.user, listing__status="OPEN"
    )    
    if request.method == 'POST':
        enrolment_request.status = "ACCEPTED"
        enrolment_request.listing.status = "RESERVED"
        enrolment_request.listing.save()
        enrolment_request.decided_at = timezone.now()
        enrolment_request.pay_by = timezone.now() + timedelta(hours=48)
        enrolment_request.save()
    return redirect('tutor_requests_view')

@login_required
def tutor_decline_request_view(request, pk):
    if request.user.role != "TUTOR":
        return redirect('index')
    enrolment_request = get_object_or_404(
        EnrolmentRequest, pk=pk, status="PENDING", listing__tutor__user=request.user
    )    
    if request.method == 'POST':
        enrolment_request.status = "DECLINED"
        enrolment_request.decided_at = timezone.now()
        reason = request.POST.get("decline_reason", "")
        enrolment_request.decline_reason = reason
        enrolment_request.save()
        return redirect('tutor_requests_view')
    else:
        return render(request, 'enrolments/tutor_decline_request_view.html', {'enrolment_request': enrolment_request})

# parent view my lessons
@login_required
def parent_view_my_lessons(request):
    if request.user.role != 'PARENT':
        return redirect('index')
    
    show = request.GET.get("show")
    child_choice = request.GET.get("child")
    if child_choice and not child_choice.isdigit():
        child_choice = None

    lessons = Lesson.objects.filter(
        package__enrolment_request__child__parent=request.user
    )
    if child_choice:
        lessons = lessons.filter(package__enrolment_request__child__id=child_choice)
    
    upcoming_lessons = lessons.filter(
        status="SCHEDULED",
        date__gte=timezone.localdate()
    ).order_by("date", "start_time")
    
    past_lessons = lessons.exclude(
        status="SCHEDULED",
        date__gte=timezone.localdate()
    ).order_by("-date", "-start_time")
    
    children = Child.objects.filter(
        parent=request.user
    )
        
    return render(request, "enrolments/parent_view_my_lessons.html",
                  {"upcoming_lessons": upcoming_lessons,
                   "past_lessons": past_lessons,
                   "show": show,
                   "child_choice": child_choice,
                   "children": children})

# tutor view schedule
@login_required
def tutor_view_my_schedule(request):
    if request.user.role != 'TUTOR':
        return redirect('index')
    
    show = request.GET.get("show")

    lessons = Lesson.objects.filter(
        package__enrolment_request__listing__tutor__user=request.user
    )
    
    upcoming_lessons = lessons.filter(
        status="SCHEDULED",
        date__gte=timezone.localdate()
    ).order_by("date", "start_time")
    
    past_lessons = lessons.exclude(
        status="SCHEDULED",
        date__gte=timezone.localdate()
    ).order_by("-date", "-start_time")
    
    
    return render(
        request,
        "enrolments/tutor_view_my_schedule.html",
        {"upcoming_lessons": upcoming_lessons,
         "past_lessons": past_lessons,
         "show": show}
    )
    
@login_required
def tutor_complete_lesson_view(request, pk):
    if request.user.role != 'TUTOR':
        return redirect('index')
    
    lesson = get_object_or_404(
        Lesson,
        pk=pk,
        status="SCHEDULED",
        package__enrolment_request__listing__tutor__user=request.user
    )
    
    if request.method == 'POST':
        if lesson.date > timezone.localdate():
            return redirect("tutor_view_my_schedule")
        lesson.status="COMPLETED"
        lesson.completed_at=timezone.now()
        lesson.save()
        
        remaining = lesson.package.lessons.filter(status="SCHEDULED").exists()
        if not remaining:
            lesson.package.status="COMPLETED"
            lesson.package.save()
        
    return redirect('tutor_view_my_schedule')