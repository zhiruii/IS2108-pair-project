from django.db import models
from accounts.models import Child
from listings.models import Listing
from django.utils import timezone
from django.core.exceptions import ValidationError

# models:
# EnrolmentRequest
# Package
# Lesson
# RescheduleRequest


class EnrolmentRequest(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
        ("WITHDRAWN", "Withdrawn"),
        ("PAID", "Paid"),
        ("EXPIRED", "Expired"),
    ]

    # a child with enrolment requests cannot be deleted
    child = models.ForeignKey(
        Child, on_delete=models.RESTRICT, related_name="enrolment_requests"
    )
    # a listing with requests can’t be deleted
    listing = models.ForeignKey(
        Listing, on_delete=models.RESTRICT, related_name="enrolment_requests"
    )
    start_date = models.DateField()
    message = models.TextField(blank=True)  # optional
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)  # empty until it happens
    pay_by = models.DateTimeField(null=True, blank=True)  # empty until accepted
    withdraw_reason = models.TextField(blank=True)  # optional
    decline_reason = models.TextField(blank=True)  # optional
    
    def __str__(self):
        return f"{self.child.first_name}: {self.listing}"
    
    def clean(self):
        # start date must be on the listing's weekday
        if self.listing_id is not None and self.start_date is not None:
            if self.start_date.weekday() != self.listing.weekday:
                raise ValidationError({
                    'start_date' : f'Start date must be a {self.listing.get_weekday_display()}.'
                })
        
        # start date cannot be in the past
        if self.start_date is not None:
            if self.start_date <= timezone.localdate():
                raise ValidationError({
                    'start_date' : 'Start date must be after today.'
                })

