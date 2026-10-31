from django.utils import timezone
from .models import EnrolmentRequest


def expire_overdue_requests():
    overdue = EnrolmentRequest.objects.filter(
        status="ACCEPTED",
        pay_by__lt=timezone.now(),
    )
    for r in overdue:
        # request → "EXPIRED", save
        r.status="EXPIRED"
        r.save()
        # its listing → "OPEN", save
        r.listing.status="OPEN"
        r.listing.save()