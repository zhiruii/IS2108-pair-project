from django.db import models
from accounts.models import LEVEL_CHOICES, TutorProfile
from django.core.exceptions import ValidationError


class Listing(models.Model):
    SUBJECT_CHOICES = [
        ("ENGLISH", "English"),
        ("CHINESE", "Chinese"),
        ("MALAY", "Malay"),
        ("TAMIL", "Tamil"),
        ("MATH", "Mathematics"),
        ("E_MATH", "E-Math"),
        ("A_MATH", "A-Math"),
        ("H2_MATH", "H2 Math"),
        ("SCIENCE", "Science"),
        ("PHYSICS", "Physics"),
        ("CHEMISTRY", "Chemistry"),
        ("BIOLOGY", "Biology"),
        ("ECONOMICS", "Economics"),
        ("GEOGRAPHY", "Geography"),
        ("HISTORY", "History"),
        ("LITERATURE", "Literature"),
    ]

    WEEKDAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    MODE_CHOICES = [
        ("IN_PERSON", "In person"),
        ("ONLINE", "Online"),
        ("HYBRID", "Hybrid")
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("FILLED", "Filled"),
        ("CLOSED", "Closed"),
    ]

    # when a tutor is deleted, their listing is deleted too
    tutor = models.ForeignKey(
        TutorProfile, on_delete=models.CASCADE, related_name="listings"
    )
    subject = models.CharField(max_length=10, choices=SUBJECT_CHOICES)
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES)
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    mode = models.CharField(max_length=9, choices=MODE_CHOICES)
    rate_per_hour = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # rate must be more than 0
            models.CheckConstraint(
                condition=models.Q(rate_per_hour__gt=0),
                name="listing_rate_per_hour_greater_than_zero",
            ),
            # lesson must end after it starts
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="listing_end_after_start",
            ),
        ]

    def clean(self):
        if (
            self.weekday is not None
            and self.tutor_id is not None
            and self.start_time
            and self.end_time
        ):
            clashes = (
                Listing.objects.filter(
                    tutor=self.tutor,
                    weekday=self.weekday,
                    start_time__lt=self.end_time,
                    end_time__gt=self.start_time,
                )
                .exclude(status="CLOSED")
                .exclude(pk=self.pk)
            )

            if clashes.exists():
                raise ValidationError(
                    "This slot overlaps another of your listings on the same day."
                )

    def __str__(self):
        return f"{self.get_subject_display()} ({self.level}) - {self.get_weekday_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}"
