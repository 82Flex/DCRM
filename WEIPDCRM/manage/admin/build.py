# coding:utf-8

"""
DCRM - Darwin Cydia Repository Manager
Copyright (C) 2017  WU Zheng <i.82@me.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from django.contrib import admin
from preferences import preferences
from django.contrib.admin.actions import delete_selected

from WEIPDCRM.models.build import Build


class BuildAdmin(admin.ModelAdmin):
    def active_release_(self, instance):
        """
        Show current active release before build a new package list.
        
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
        Set the active release, call building procedure, and then save.
        :type obj: Build
        """
        obj.active_release = preferences.Setting.active_release
        super(BuildAdmin, self).save_model(request, obj, form, change)
