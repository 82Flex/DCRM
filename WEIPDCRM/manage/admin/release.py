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
from django.contrib import messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from suit import apps
from suit.widgets import AutosizedTextarea

from preferences import preferences


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
        (_('General'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['origin', 'label', 'version', 'codename']
        }),
        (_('Appearance'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['icon', 'description']
        }),
        (_('History'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['created_at']
        }),
        # Advanced
        (_('Cydia'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['suite', 'components', "support", "email"]
        }),
        (_('SEO'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['keywords']
        }),
    ]
    suit_form_size = {
        'widgets': {
            'AutosizedTextarea': apps.SUIT_FORM_SIZE_X_LARGE,
        },
    }
    suit_form_tabs = (
        ('common', _('Common')),
        ('advanced', _('Advanced')),
    )
    
    def save_model(self, request, obj, form, change):
        super(ReleaseAdmin, self).save_model(request, obj, form, change)
        if not preferences.Setting.active_release:
            messages.warning(request, mark_safe(_(
                "There is no active release. " +
                "<a href=\"%s\">" +
                "Set current release as active release." +
                "</a>"
            ) % reverse("set_default_release", args=[obj.id])))
    
    change_form_template = "admin/release/change_form.html"
