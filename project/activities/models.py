import datetime
from enum import Enum

from circles.models import Circle
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Activity(models.Model):
    class ActivityTypeIcons(Enum):
        APPOINTMENT = "bi-calendar-event"
        CALL = "bi-camera-video"
        ENTERTAINMENT = "bi-ticket-perforated"
        ERRAND = "bi-building"
        HOUSEWORK = "bi-house"
        NATURE = "bi-tree"
        OUTING = "bi-cup-straw"
        SHOPPING = "bi-cart"

    class ActivityTypeChoices(models.TextChoices):
        APPOINTMENT = "APPOINTMENT", _("Appointment")
        CALL = "CALL", _("Call")
        ENTERTAINMENT = "ENTERTAINMENT", _("Entertainment")
        ERRAND = "ERRAND", _("Errand")
        HOUSEWORK = "HOUSEWORK", _("Housework")
        NATURE = "NATURE", _("Nature")
        OUTING = "OUTING", _("Outing")
        SHOPPING = "SHOPPING", _("Shopping")

    activity_type = models.CharField(
        max_length=15,
        choices=ActivityTypeChoices.choices,
        default=ActivityTypeChoices.APPOINTMENT,
    )

    activity_date = models.DateField(default=datetime.date.today)

    note = models.CharField(
        max_length=50,
        help_text=_(
            "Optionally, add a brief note. For privacy, avoid adding sensitive information."  # noqa: E501
        ),
        null=True,
        blank=True,
    )

    circle = models.ForeignKey(
        to=Circle,
        related_name="activities",
        on_delete=models.CASCADE,
        null=True,
    )

    participants = models.ManyToManyField(User, related_name="activities")

    done = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        ordering = [
            "activity_date",
        ]

    def __str__(self):
        return self.get_activity_type_display()

    def get_absolute_url(self):
        return reverse("activity-detail", kwargs={"pk": self.pk})

    @property
    def icon(self):
        return self.ActivityTypeIcons[self.activity_type].value

    @property
    def remaining_eligible_companions(self):
        """Return a QuerySet of the circle's companions who are not already activity participants."""  # noqa: E501
        # Only care group members are eligible to participate
        companions = self.circle.companions

        # Get current activity participants
        current_participants = self.participants.all()

        # Exclude existing companions from care group members
        remaining_eligible_companions = companions.difference(current_participants)

        return remaining_eligible_companions


class Comment(models.Model):
    user_id = models.BigIntegerField()
    text = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    activity = models.ForeignKey(
        to=Activity,
        related_name="comment",
        on_delete=models.CASCADE,
        null=True,
    )
