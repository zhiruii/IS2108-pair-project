from django.db import models
from accounts.models import Child
from listings.models import Listing
from django.utils import timezone
from django.core.exceptions import ValidationError

# models:
# EnrolmentRequest (DONE)
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
                raise ValidationError(
                    {
                        "start_date": f"Start date must be a {self.listing.get_weekday_display()}."
                    }
                )

        # start date cannot be in the past
        if self.start_date is not None:
            if self.start_date <= timezone.localdate():
                raise ValidationError({"start_date": "Start date must be after today."})


class Package(models.Model):

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    # one package per request; a renewal creates a new request
    # a request that has a package can’t be deleted, which protects payment records
    enrolment_request = models.OneToOneField(
        EnrolmentRequest, on_delete=models.RESTRICT, related_name="package"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    lesson_count = models.PositiveIntegerField(default=4)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default="ACTIVE")
    # if an old package is deleted, the renewal should lose its link
    renewal_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="renewals",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # end date is on or after the start date
            models.CheckConstraint(
                condition=models.Q(end_date__gte=models.F("start_date")),
                name="package_end_date_greater_than_or_equal_to_start_date",
            ),
            # lesson count is above 0
            models.CheckConstraint(
                condition=models.Q(lesson_count__gt=0),
                name="package_lesson_count_greater_than_0",
            ),
            # total price is above 0
            models.CheckConstraint(
                condition=models.Q(total_price__gt=0),
                name="package_total_price_greater_than_0",
            ),
        ]

    def __str__(self):
        return f"Package #{self.pk}: {self.enrolment_request.child.first_name}, {self.enrolment_request.listing}"
