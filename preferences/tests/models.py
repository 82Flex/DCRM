from django.db import models
from preferences.models import Preferences


class MyPreferences(Preferences):
    portal_contact_email = models.EmailField()
