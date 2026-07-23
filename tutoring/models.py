from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TutorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_profile"
    )
    bio = models.TextField(blank=True)
    subjects = models.ManyToManyField(Subject, related_name="tutors", blank=True)

    def __str__(self):
        return f"TutorProfile({self.user.username})"


class Availability(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="availabilities")
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.tutor} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class SessionRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("completed", "Completed"),
    ]
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requested_sessions"
    )
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="session_requests")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    proposed_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} -> {self.tutor} ({self.status})"
