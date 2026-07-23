from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Subject, TutorProfile, Availability, SessionRequest
from .serializers import (
    SubjectSerializer,
    TutorProfileSerializer,
    AvailabilitySerializer,
    SessionRequestSerializer,
)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TutorProfileViewSet(viewsets.ModelViewSet):
    queryset = TutorProfile.objects.all()
    serializer_class = TutorProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["subjects__name", "user__username"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AvailabilityViewSet(viewsets.ModelViewSet):
    """Lets a logged-in tutor manage their own availability slots."""

    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Availability.objects.filter(tutor__user=self.request.user)

    def _get_own_profile(self):
        try:
            return self.request.user.tutor_profile
        except TutorProfile.DoesNotExist:
            raise ValidationError("You need a tutor profile before adding availability.")

    def perform_create(self, serializer):
        serializer.save(tutor=self._get_own_profile())

    def perform_update(self, serializer):
        if serializer.instance.tutor.user != self.request.user:
            raise PermissionDenied("You can only edit your own availability.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.tutor.user != self.request.user:
            raise PermissionDenied("You can only delete your own availability.")
        instance.delete()


class SessionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SessionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return SessionRequest.objects.filter(student=user) | SessionRequest.objects.filter(tutor__user=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def _require_tutor_side(self, session):
        if session.tutor.user != self.request.user:
            raise PermissionDenied("Only the assigned tutor can do that.")

    @action(detail=True, methods=["patch"])
    def accept(self, request, pk=None):
        session = self.get_object()
        self._require_tutor_side(session)
        session.status = "accepted"
        session.save()
        return Response(self.get_serializer(session).data)

    @action(detail=True, methods=["patch"])
    def decline(self, request, pk=None):
        session = self.get_object()
        self._require_tutor_side(session)
        session.status = "declined"
        session.save()
        return Response(self.get_serializer(session).data)

    @action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        session = self.get_object()
        self._require_tutor_side(session)
        if session.status != "accepted":
            raise ValidationError("Only accepted sessions can be marked complete.")
        if timezone.now() < session.proposed_time:
            raise ValidationError(
                "This session hasn't happened yet — you can mark it complete once its scheduled time has passed."
            )
        session.status = "completed"
        session.save()
        return Response(self.get_serializer(session).data)
