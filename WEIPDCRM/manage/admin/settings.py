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

from preferences.admin import PreferencesAdmin
from django.forms import ModelForm
from suit.widgets import AutosizedTextarea
from suit_redactor.widgets import RedactorWidget
from django.utils.translation import ugettext_lazy as _


class SettingsForm(ModelForm):
    class Meta(object):
        widgets = {
            'notice': RedactorWidget,
            'advertisement': RedactorWidget,
            'external_statistics': AutosizedTextarea,
            'internal_statistics': AutosizedTextarea
        }


class SettingsAdmin(PreferencesAdmin):
    form = SettingsForm
    fieldsets = [
        (_('General'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['active_release']
        }),
        (_('Packages List'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['enable_pdiffs', 'gpg_signature', 'packages_compression',
                       'packages_validation', 'downgrade_support']
        }),
        # Frontend
        (_('Display'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['advanced_mode', 'version_history', 'enable_comments', 'favicon',
                       'notice', 'advertisement']
        }),
        (_('Social'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['display_social', 'qq_group_name', 'qq_group_url',
                       'weibo_name', 'weibo_url',  'telegram_name', 'telegram_url', 'alipay_url',
                       'twitter_name', 'twitter_url', 'facebook_name', 'facebook_url', 'paypal_url']
        }),
        (_('Statistics'),{
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['external_statistics', 'internal_statistics']
        }),
        (_('Footer'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['copyright_name', 'copyright_year',
                       'footer_icp']
        }),
        # Advanced
        (_('Resource'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['atomic_storage', 'resources_alias']
        }),
        (_('Server'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['web_server', 'redirect_resources', 'redirect_prefix',
                       'download_count', 'download_cydia_only']
        }),
        # Rest API
        (_('Global'), {
            'classes': ('suit-tab suit-tab-api',),
            'fields': ['rest_api']
        }),
        # Third Party
    ]

    suit_form_tabs = (
        ('common', _('Common')),
        ('advanced', _('Advanced')),
        ('frontend', _('Frontend')),
        ('api', _('Rest API')),
        ('third-party', _('Third-Party')),
    )

    def has_add_permission(self, request):
        """
        This is a single instance so you cannot add or delete it.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    change_form_template = "admin/setting/change_form.html"
