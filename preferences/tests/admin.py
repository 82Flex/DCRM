from django.contrib import admin

from preferences.admin import PreferencesAdmin
from preferences.tests.models import MyPreferences

admin.site.register(MyPreferences, PreferencesAdmin)
