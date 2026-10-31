from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from enrolments.models import EnrolmentRequest
from datetime import datetime, timedelta
from decimal import Decimal


# Create your views here.
@login_required
def parent_pay_view(request, pk):
    if request.user.role != "PARENT":
        return redirect("index")

    req_to_pay = get_object_or_404(
        EnrolmentRequest, pk=pk, status="ACCEPTED", child__parent=request.user
    )

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
