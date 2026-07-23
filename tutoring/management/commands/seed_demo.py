import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tutoring.models import Subject, TutorProfile, Availability, SessionRequest

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with demo data: 4 subjects, 4 tutors, 4 students, and sample sessions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo data before seeding (safe to re-run before a presentation).",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("Clearing existing demo data...")
            SessionRequest.objects.all().delete()
            Availability.objects.all().delete()
            TutorProfile.objects.all().delete()
            User.objects.filter(username__startswith="tutor_").delete()
            User.objects.filter(username__startswith="student_").delete()
            Subject.objects.all().delete()

        # --- Subjects ---
        subject_names = ["Mathematics", "Chemistry", "Python Programming", "English Literature"]
        subjects = [Subject.objects.get_or_create(name=name)[0] for name in subject_names]
        self.stdout.write(self.style.SUCCESS(f"Created {len(subjects)} subjects."))

        # --- Tutors ---
        tutor_data = [
            ("tutor_brian", "Brian", "Otieno", "3rd year Math major, loves calculus and algebra.", [0]),
            ("tutor_wakaria", "Wakaria", "Muthoni", "Chemistry TA, focuses on organic chemistry basics.", [1]),
            ("tutor_ruger", "Ruger", "Kimani", "Backend dev, teaches Python from scratch.", [2]),
            ("tutor_glenn", "Glenn", "Odhiambo", "English lit tutor, essay structure specialist.", [3]),
        ]
        tutors = []
        for username, first, last, bio, subject_idxs in tutor_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@demo.com",
                    "first_name": first,
                    "last_name": last,
                    "is_tutor": True,
                    "is_student": False,
                },
            )
            if created:
                user.set_password("demopass123")
                user.save()

            profile, _ = TutorProfile.objects.get_or_create(user=user, defaults={"bio": bio})
            profile.bio = bio
            profile.save()
            profile.subjects.set([subjects[i] for i in subject_idxs])

            Availability.objects.get_or_create(
                tutor=profile,
                day_of_week=1,
                start_time=datetime.time(17, 0),
                end_time=datetime.time(19, 0),
            )
            Availability.objects.get_or_create(
                tutor=profile,
                day_of_week=3,
                start_time=datetime.time(14, 0),
                end_time=datetime.time(16, 0),
            )
            tutors.append(profile)

        self.stdout.write(self.style.SUCCESS(f"Created {len(tutors)} tutor profiles with availability."))

        # --- Students ---
        student_data = [
            ("student_ethan", "Ethan", "Mwangi"),
            ("student_leo", "Leo", "Njoroge"),
            ("student_phabian", "Phabian", "Kariuki"),
            ("student_lewis", "Lewis", "Omondi"),
        ]
        students = []
        for username, first, last in student_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@demo.com",
                    "first_name": first,
                    "last_name": last,
                    "is_tutor": False,
                    "is_student": True,
                },
            )
            if created:
                user.set_password("demopass123")
                user.save()
            students.append(user)

        self.stdout.write(self.style.SUCCESS(f"Created {len(students)} student accounts."))

        # --- Sample session requests (pending, accepted, completed) ---
        now = timezone.now()
        sample_sessions = [
            (students[0], tutors[0], subjects[0], now + datetime.timedelta(days=1), "pending", "Need help with derivatives"),
            (students[1], tutors[1], subjects[1], now + datetime.timedelta(days=2), "accepted", "Struggling with balancing equations"),
            (students[2], tutors[2], subjects[2], now - datetime.timedelta(days=3), "completed", "Debugging a Flask app"),
            (students[3], tutors[3], subjects[3], now + datetime.timedelta(days=1), "pending", "Essay structure for Macbeth"),
        ]
        created_count = 0
        for student, tutor, subject, when, status, notes in sample_sessions:
            _, created = SessionRequest.objects.get_or_create(
                student=student,
                tutor=tutor,
                subject=subject,
                proposed_time=when,
                defaults={"status": status, "notes": notes},
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} sample session requests."))
        self.stdout.write(self.style.SUCCESS("Demo seed complete. All demo accounts use password: demopass123"))
