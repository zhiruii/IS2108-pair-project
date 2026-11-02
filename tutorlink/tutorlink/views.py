from django.shortcuts import render
from enrolments.models import Lesson, EnrolmentRequest, Package
from enrolments.utils import expire_overdue_requests
from django.utils import timezone

def index(request):
    context = {}
    if request.user.is_authenticated and request.user.role == "PARENT":
        expire_overdue_requests()

        lessons = Lesson.objects.filter(
            package__enrolment_request__child__parent=request.user
        )

        upcoming_lessons = lessons.filter(
            status="SCHEDULED", date__gte=timezone.localdate()
        ).order_by("date", "start_time")
        
        next_lesson = upcoming_lessons.first()
        
        to_pay = EnrolmentRequest.objects.filter(
            child__parent=request.user,
            status="ACCEPTED"
        ).order_by("pay_by")
        
        pending_count = EnrolmentRequest.objects.filter(
            child__parent=request.user,
            status="PENDING"
        ).count()
        
        to_rate = Package.objects.filter(
            enrolment_request__child__parent=request.user,
        ).exclude(
            lessons__status="SCHEDULED" # exclude if still have lessons left
        ).exclude(
            ratings__rater=request.user # already rated
        ).select_related("enrolment_request__listing", "enrolment_request__child__parent")
        
        context={'next_lesson': next_lesson, 'to_pay': to_pay, 'pending_count': pending_count, 'to_rate': to_rate}

    elif request.user.is_authenticated and request.user.role == "TUTOR":
        expire_overdue_requests()

        lessons = Lesson.objects.filter(
            package__enrolment_request__listing__tutor__user=request.user
        )

        next_lesson = lessons.filter(
            status="SCHEDULED", date__gte=timezone.localdate()
        ).order_by("date", "start_time").first()

        to_mark = lessons.filter(
            status="SCHEDULED", date__lt=timezone.localdate()   # BEFORE today
        ).count()

        request_count = EnrolmentRequest.objects.filter(
            listing__tutor__user=request.user,         # requests on this tutor's listings
            status="PENDING"
        ).count()
        
        to_rate = Package.objects.filter(
            enrolment_request__listing__tutor__user=request.user,
        ).exclude(
            lessons__status="SCHEDULED" # exclude if still have lessons left
        ).exclude(
            ratings__rater=request.user # already rated
        ).select_related("enrolment_request__listing__tutor__user", "enrolment_request__child")

        context = {"next_lesson": next_lesson, "to_mark": to_mark, "request_count": request_count, "to_rate": to_rate} 
    
    return render(request, 'index.html', context)