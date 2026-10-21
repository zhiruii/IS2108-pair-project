from django.db import models
from django.conf import settings
from accounts.models import TutorProfile, Child
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
    # the child being rated
    rated_child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,  # if child is deleted, all his ratings deleted too
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
            # one rating per rater per package
            models.UniqueConstraint(
                fields=["rater", "package"],
                name="rating_one_rating_per_rater_per_package",
            ),
            # exactly one of rated_tutor / rated_child
            models.CheckConstraint(
                condition=(
                    models.Q(rated_tutor__isnull=False, rated_child__isnull=True)
                    | models.Q(rated_tutor__isnull=True, rated_child__isnull=False)
                ),
                name="rating_exactly_one_target",
            ),
        ]

    def clean(self):
        # rating is only allowed after the package has at least one completed lesson
        if self.package_id is not None:
            if not self.package.lessons.filter(status="COMPLETED").exists():
                raise ValidationError(
                    "Rating is only allowed after the package has at least one completed lesson."
                )

    def __str__(self):
        if self.rated_tutor is not None:
            target = self.rated_tutor.user
        else:
            target = self.rated_child.first_name
        return f"{self.stars}/5 rating from {self.rater} to {target} (Package #{self.package_id})"
