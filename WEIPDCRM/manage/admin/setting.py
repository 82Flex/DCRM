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

from django.contrib.sites.models import Site
from django.conf import settings
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from preferences.admin import PreferencesAdmin
from suit.widgets import AutosizedTextarea
from suit_redactor.widgets import RedactorWidget


class SettingForm(ModelForm):
    class Meta(object):
        widgets = {
            'notice': RedactorWidget,
            'advertisement': RedactorWidget,
            'external_statistics': AutosizedTextarea,
            'internal_statistics': AutosizedTextarea
        }


class SettingAdmin(PreferencesAdmin):
    def site_(self, instance):
        return mark_safe(
            _("<a href=\"%(href)s\" target=\"_blank\">%(name)s</a>")
            % ({
                "href": reverse("admin:sites_site_change", args=[settings.SITE_ID]),
                "name": Site.objects.get(id=settings.SITE_ID)
            })
        )
    site_.short_description = _("Current Site")

    def redis_(self, instance):
        if settings.ENABLE_REDIS:
            return _("Enabled (in DCRM/settings.py)")
        else:
            return _("Disabled (in DCRM/settings.py)")
    redis_.short_description = _("Redis Status")

    def memcached_(self, instance):
        if settings.ENABLE_CACHE:
            return _("Enabled (in DCRM/settings.py)")
        else:
            return _("Disabled (in DCRM/settings.py)")
    memcached_.short_description = _("Memcached Status")

    def api_(self, instance):
        if settings.ENABLE_API:
            return _("Enabled (in DCRM/settings.py)")
        else:
            return _("Disabled (in DCRM/settings.py)")
    api_.short_description = _("API Status")

    form = SettingForm
    readonly_fields = [
        'site_',
        'redis_',
        'memcached_',
        'api_'
    ]
    fieldsets = [
        (_('General'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['site_', 'active_release']
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
        (_('Queue'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['redis_']
        }),
        (_('Cache'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['memcached_']
        }),
        (_('API'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['api_']
        }),
        # Third Party
    ]

    suit_form_tabs = (
        ('common', _('Common')),
        ('advanced', _('Advanced')),
        ('frontend', _('Frontend')),
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
