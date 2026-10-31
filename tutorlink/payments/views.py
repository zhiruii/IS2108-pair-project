from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from enrolments.models import EnrolmentRequest
from datetime import datetime, timedelta
from decimal import Decimal
from .forms import PaymentForm
from enrolments.models import Lesson, Package
from enrolments.utils import expire_overdue_requests

def get_price_summary(req_to_pay):
    lesson_dates = [req_to_pay.start_date + timedelta(days=7 * i) for i in range(4)]

    hours = (
        Decimal(
            (
                datetime.combine(req_to_pay.start_date, req_to_pay.listing.end_time)
                - datetime.combine(req_to_pay.start_date, req_to_pay.listing.start_time)
            ).total_seconds()
        )
        / 3600
    )
    price_per_lesson = (req_to_pay.listing.rate_per_hour * hours).quantize(
        Decimal("0.01")
    )

    total_price = price_per_lesson * 4
    
    return lesson_dates, price_per_lesson, total_price

# Create your views here.
@login_required
def parent_pay_view(request, pk):
    if request.user.role != "PARENT":
        return redirect("index")
    
    expire_overdue_requests()

    req_to_pay = get_object_or_404(
        EnrolmentRequest, pk=pk, status="ACCEPTED", child__parent=request.user
    )
    
    lesson_dates, price_per_lesson, total_price = get_price_summary(req_to_pay)

    return render(
        request,
        "payments/parent_pay_view.html",
        {
            "req_to_pay": req_to_pay,
            "lesson_dates": lesson_dates,
            "price_per_lesson": price_per_lesson,
            "total_price": total_price,
        },
    )
    
@login_required
def parent_payment_view(request, pk):
    if request.user.role != 'PARENT':
        return redirect('index')
    
    expire_overdue_requests()

    req_to_pay = get_object_or_404(
        EnrolmentRequest, pk=pk, status="ACCEPTED", child__parent=request.user
    )
    lesson_dates, price_per_lesson, total_price = get_price_summary(req_to_pay)
    if request.method == 'GET':
        form = PaymentForm()
    else:
        form = PaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                package = Package.objects.create(
                enrolment_request=req_to_pay,
                start_date=lesson_dates[0],          # first lesson date
                end_date=lesson_dates[-1],            # last lesson date: lesson_dates[-1]
                lesson_count=4,
                total_price=total_price,
            )
                commission = (price_per_lesson * Decimal("0.05")).quantize(Decimal("0.01"))
                for d in lesson_dates:
                    Lesson.objects.create(
                        package=package,
                        date=d,
                        start_time=req_to_pay.listing.start_time,      # from the listing
                        end_time=req_to_pay.listing.end_time,
                        price=price_per_lesson,
                        commission=commission,
                        tutor_amount=price_per_lesson-commission,    # price minus commission
                    )

                req_to_pay.status="PAID"
                req_to_pay.listing.status="FILLED"
                req_to_pay.save()
                req_to_pay.listing.save()
            return redirect('payment_success_view', package.pk)
    
    return render(
        request, "payments/parent_payment_view.html",
        {'form': form,
         'req_to_pay': req_to_pay,
         'total_price': total_price})

@login_required
def payment_success_view(request, pk):
    if request.user.role != 'PARENT':
        return redirect('index')
    package = get_object_or_404(
        Package, pk=pk, enrolment_request__child__parent=request.user
    )
    return render(
        request,
        "payments/payment_success_view.html",
        {"package": package}
    )

@login_required
def payment_history_view(request):
    if request.user.role != 'PARENT':
        return redirect('index')
    packages = Package.objects.filter(enrolment_request__child__parent=request.user).order_by("-created_at")
    return render(request, "payments/parent_payment_history_view.html", {"packages": packages})

@login_required
def tutor_earnings_view(request):
    if request.user.role != 'TUTOR':
        return redirect('index')
    
    lessons = Lesson.objects.filter(package__enrolment_request__listing__tutor__user=request.user)
    
    completed = lessons.filter(status="COMPLETED").order_by("-completed_at")
    upcoming = lessons.filter(status="SCHEDULED")
    
    totals = completed.aggregate(
        earned=Sum("tutor_amount"),
        commission=Sum("commission"),
    )
    
    pending_earnings = upcoming.aggregate(
        earned=Sum("tutor_amount"),
        commission=Sum("commission")
    )
    
    return render(request, "payments/tutor_earnings_view.html", 
                  {'completed': completed,
                   'totals': totals,
                   'upcoming': upcoming,
                   'pending_earnings': pending_earnings})