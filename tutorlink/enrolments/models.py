from django.db import models
from accounts.models import Child
from listings.models import Listing
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime, timedelta

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


class Lesson(models.Model):

    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("RESCHEDULED", "Rescheduled"),
    ]

    # many lessons per package -> ForeignKey
    package = models.ForeignKey(
        Package,
        related_name="lessons",
        # if a package has lessons, it cannot be deleted
        on_delete=models.RESTRICT,
    )
    date = models.DateField()
    # give each lesson its own time columns that are initially empty
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=11, choices=STATUS_CHOICES, default="SCHEDULED"
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    commission = models.DecimalField(max_digits=6, decimal_places=2)
    tutor_amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        request = self.package.enrolment_request
        return f"{request.child.first_name}: {request.listing.get_subject_display()}, {self.date:%a %d %b} {self.start_time:%H:%M}-{self.end_time:%H:%M} [{self.get_status_display()}]"

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            # end time is after the start time
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="lesson_end_time_greater_than_start_time",
            ),
            # price is above 0
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="lesson_price_greater_than_0",
            ),
            # commission + tutor_amount = price
            models.CheckConstraint(
                condition=models.Q(
                    price=models.F("commission") + models.F("tutor_amount")
                ),
                name="lesson_commission_and_tutor_amount_equals_price",
            ),
        ]


class RescheduleRequest(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
        ("EXPIRED", "Expired"),
    ]

    # a lesson with reschedule requests can’t be deleted, which keeps its history
    lesson = models.ForeignKey(
        Lesson, on_delete=models.RESTRICT, related_name="reschedule_requests"
    )
    # if the user who proposed it is deleted, the request goes with them
    # (users with bookings are already blocked from deletion)
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reschedule_requests",
    )
    new_date = models.DateField()
    new_start_time = models.TimeField()
    new_end_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # new end time is after new start time
            models.CheckConstraint(
                condition=models.Q(new_end_time__gt=models.F("new_start_time")),
                name="rescheduled_req_end_time_greater_than_start_time",
            ),
        ]

    def __str__(self):
        return f"Reschedule {self.lesson} -> {self.new_date:%a %d %b} {self.new_start_time:%H:%M}-{self.new_end_time:%H:%M} [{self.get_status_display()}]"

    def clean(self):
        # the request must be made at least 24 hours before the lesson
        if self.lesson_id is not None and self.pk is None:
            lesson_start = datetime.combine(self.lesson.date, self.lesson.start_time)
            lesson_start = timezone.make_aware(lesson_start)
            if timezone.now() > lesson_start - timedelta(hours=24):
                raise ValidationError(
                    "Reschedule requests must be made at least 24 hours before the lesson."
                )
        # the new slot must be in the future
        if self.new_date and self.new_start_time and self.pk is None:
            new_start = datetime.combine(self.new_date, self.new_start_time)
            new_start = timezone.make_aware(new_start)
            if new_start < timezone.now():
                raise ValidationError(
                    "The new lesson time must be in the future."
                )