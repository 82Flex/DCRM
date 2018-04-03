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
from django.utils.translation import ugettext_lazy as _


class OSVersionAdmin(admin.ModelAdmin):
    actions = [delete_selected]
    list_display = ('descriptor', 'build', 'created_at')
    search_fields = ['descriptor', 'build']
    readonly_fields = ['created_at']
    fieldsets = [
        (_('General'), {
            'fields': ['enabled', 'descriptor', 'build']
        }),
        (_('Appearance'), {
            'fields': ['icon']
        }),
        (_('History'), {
            'fields': ['created_at']
        }),
    ]
    change_form_template = "admin/os_version/change_form.html"
