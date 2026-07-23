from django.contrib import admin
from .models import Subject, TutorProfile, Availability, SessionRequest

admin.site.register(Subject)
admin.site.register(TutorProfile)
admin.site.register(Availability)
admin.site.register(SessionRequest)
