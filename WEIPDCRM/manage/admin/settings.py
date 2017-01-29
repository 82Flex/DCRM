# coding:utf-8

from preferences.admin import PreferencesAdmin


class SettingsAdmin(PreferencesAdmin):
    fieldsets = [
        ('General', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['active_release']
        }),
        ('Packages List', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['packages_compression', 'packages_validation', 'downgrade_support']
        }),
        ('Cydia', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['advanced_mode']
        }),
    ]

    suit_form_tabs = (
        ('common', 'Common'),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
