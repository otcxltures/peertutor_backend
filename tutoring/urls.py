from rest_framework.routers import DefaultRouter

from .views import SubjectViewSet, TutorProfileViewSet, AvailabilityViewSet, SessionRequestViewSet

router = DefaultRouter()
router.register("subjects", SubjectViewSet)
router.register("tutors", TutorProfileViewSet)
router.register("availability", AvailabilityViewSet, basename="availability")
router.register("sessions", SessionRequestViewSet, basename="session")

urlpatterns = router.urls
