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
from django.contrib.admin.actions import delete_selected
from django.utils.translation import ugettext as _

from WEIPDCRM.models.section import Section
from WEIPDCRM.models.version import Version

from preferences import preferences


class SectionAdmin(admin.ModelAdmin):
    def generate_icon_package(self, request, queryset):
        # TODO: Generate icon package
        self.message_user(request, _("Icon package generating job has been added to the \"default\" queue."))
    generate_icon_package.short_description = _("Generate icon package for selected sections")
    
    list_display = ('name', 'created_at')
    search_fields = ['name']
    fieldsets = [
        (_('General'), {
            'fields': ['name']
        }),
        (_('Appearance'), {
            'fields': ['icon']
        }),
        (_('History'), {
            'fields': ['created_at']
        }),
    ]
    actions = [generate_icon_package, delete_selected]
    
    def has_add_permission(self, request):
        return preferences.Setting.active_release is not None
    
    def get_readonly_fields(self, request, obj=None):
        """
        You cannot edit section name if any version has assigned to it.
        
        :type obj: Section
        """
        if obj is not None and Version.objects.filter(c_section=obj).count() > 0:
            return ['created_at', 'name']
        else:
            return ['created_at']
    
    change_form_template = 'admin/section/change_form.html'
