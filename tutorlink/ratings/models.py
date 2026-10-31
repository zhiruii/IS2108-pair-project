from django.db import models
from django.conf import settings
from accounts.models import TutorProfile
from enrolments.models import Package
from django.core.exceptions import ValidationError

# Create your models here.


class Rating(models.Model):
    # users, children and packages with bookings are already protected by RESTRICT in enrolments
    # who gave the rating
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # if rater is deleted, all his ratings deleted too
        related_name="ratings_given",
    )
    # the tutor being rated
    rated_tutor = models.ForeignKey(
        TutorProfile,
        on_delete=models.CASCADE,  # if tutor is deleted, all his ratings deleted too
        related_name="ratings_received",
        null=True,
        blank=True,
    )
    # the parent being rated
    rated_parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # if parent is deleted, all his ratings deleted too
        related_name="ratings_received",
        null=True,
        blank=True,
    )
    # which package it's for
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,  # if package is deleted, all its ratings are deleted too
        related_name="ratings",
    )
    stars = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # stars between 1 and 5
            models.CheckConstraint(
                condition=models.Q(stars__gte=1, stars__lte=5),
                name="rating_stars_between_1_and_5",
            ),
            # one rating per rater per package, one package at most 2 ratings that goes both ways
            models.UniqueConstraint(
                fields=["rater", "package"],
                name="rating_one_rating_per_rater_per_package",
            ),
            # exactly one of rated_tutor / rated_parent
            models.CheckConstraint(
                condition=(
                    models.Q(rated_tutor__isnull=False, rated_parent__isnull=True)
                    | models.Q(rated_tutor__isnull=True, rated_parent__isnull=False)
                ),
                name="rating_exactly_one_target",
            ),
        ]

    def clean(self):
        # rating is only allowed after the package has no scheduled lessons left
        if self.package_id is not None:
            lessons = self.package.lessons
            if lessons.filter(status="SCHEDULED").exists():
                raise ValidationError(
                    "Rating is only allowed after the package has no scheduled lessons left."
                )

    def __str__(self):
        if self.rated_tutor is not None:
            target = self.rated_tutor.user
        else:
            target = self.rated_parent
        return f"{self.stars}/5 rating from {self.rater} to {target} (Package #{self.package_id})"

class Dispute(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("UPHELD", "Upheld"),
        ("REJECTED", "Rejected"),
    ]

    # one dispute per rating, if the rating is deleted the dispute stays as a record
    rating = models.OneToOneField(
        Rating, on_delete=models.SET_NULL, null=True, blank=True, related_name="dispute"
    )
    # text copy of the rating, so the record still makes sense after it is deleted
    rating_summary = models.CharField(max_length=255, blank=True)
    # the person who was rated and disagrees
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="disputes_raised"
    )
    reason = models.TextField()
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="OPEN")
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="disputes_resolved",
    )

    def __str__(self):
        return f"Dispute #{self.pk} by {self.raised_by} [{self.get_status_display()}]"
