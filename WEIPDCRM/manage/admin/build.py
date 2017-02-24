# coding:utf-8

from __future__ import unicode_literals

from django.contrib import admin
from preferences import preferences
from django.contrib.admin.actions import delete_selected

from WEIPDCRM.models.build import Build


class BuildAdmin(admin.ModelAdmin):
    def active_release_(self, instance):
        """
        :type instance: Build
        """
        if instance.active_release is None:
            return unicode(preferences.Setting.active_release)
        return unicode(instance.active_release)

    actions = [delete_selected]
    list_display = ('uuid', 'active_release', 'compression', 'created_at')
    search_fields = ['uuid']
    readonly_fields = ['uuid', 'created_at', 'active_release_', 'compression', 'details']
    fieldsets = [
        ('General', {
            'fields': ['uuid', 'active_release_']
        }),
        ('Storage', {
            'fields': ['compression', 'details']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
    change_form_template = "admin/build/change_form.html"
    change_list_template = "admin/build/change_list.html"
    
    def save_model(self, request, obj, form, change):
        """
        :type obj: Build
        """
        obj.active_release = preferences.Setting.active_release
        super(BuildAdmin, self).save_model(request, obj, form, change)
