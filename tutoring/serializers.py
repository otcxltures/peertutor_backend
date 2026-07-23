from rest_framework import serializers
from .models import Subject, TutorProfile, Availability, SessionRequest


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name"]


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ["id", "day_of_week", "start_time", "end_time"]


class TutorProfileSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), many=True, write_only=True, source="subjects", required=False
    )
    availabilities = AvailabilitySerializer(many=True, read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = TutorProfile
        fields = ["id", "username", "first_name", "last_name", "bio", "subjects", "subject_ids", "availabilities"]


class SessionRequestSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    student_name = serializers.SerializerMethodField()
    tutor_username = serializers.CharField(source="tutor.user.username", read_only=True)
    tutor_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = SessionRequest
        fields = [
            "id",
            "student",
            "student_username",
            "student_name",
            "tutor",
            "tutor_username",
            "tutor_name",
            "subject",
            "subject_name",
            "proposed_time",
            "status",
            "notes",
            "created_at",
        ]

    def _display_name(self, user):
        full = f"{user.first_name} {user.last_name}".strip()
        return full or user.username

    def get_student_name(self, obj):
        return self._display_name(obj.student)

    def get_tutor_name(self, obj):
        return self._display_name(obj.tutor.user)
        read_only_fields = ["status", "student"]
