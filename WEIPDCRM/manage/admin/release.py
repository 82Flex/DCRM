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
from django.forms import ModelForm
from suit import apps
from suit.widgets import AutosizedTextarea


class ReleaseForm(ModelForm):
    class Meta(object):
        widgets = {
            'description': AutosizedTextarea,
        }


class ReleaseAdmin(admin.ModelAdmin):
    form = ReleaseForm
    actions = [delete_selected]
    list_display = ('origin', 'label', 'codename', 'version', 'created_at')
    search_fields = ['origin', 'label', 'codename']
    readonly_fields = ['created_at']
    fieldsets = [
        ('General', {
            'fields': ['origin', 'label', 'version', 'codename']
        }),
        ('Appearance', {
            'fields': ['icon', 'description']
        }),
        ('Cydia', {
            'fields': ['suite', 'components', "support"]
        }),
        ('SEO', {
            'fields': ['keywords']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
    suit_form_size = {
        'widgets': {
            'AutosizedTextarea': apps.SUIT_FORM_SIZE_X_LARGE,
        },
    }
    
    change_form_template = "admin/release/change_form.html"
