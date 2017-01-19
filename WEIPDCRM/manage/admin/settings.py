# coding:utf-8

from preferences.admin import PreferencesAdmin


class SettingsAdmin(PreferencesAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
