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
            return mark_safe(
                _("<a href=\"%(href)s\" target=\"_blank\">%(name)s</a>")
                % ({
                    "href": reverse("rq_home"),
                    "name": _("Enabled")
                })
            )
        else:
            return _("Disabled")
    redis_.short_description = _("Redis Status")

    def memcached_(self, instance):
        if settings.ENABLE_CACHE:
            return _("Enabled")
        else:
            return _("Disabled")
    memcached_.short_description = _("Memcached Status")

    def memcached_interval_(self, instance):
        return settings.CACHE_TIME
    memcached_interval_.short_description = _("Memcached Interval")

    def api_(self, instance):
        if settings.ENABLE_API:
            return mark_safe(
                _("<a href=\"%(href)s\" target=\"_blank\">%(name)s</a>")
                % ({
                    "href": reverse("api-root"),
                    "name": _("Enabled")
                })
            )
        else:
            return _("Disabled")
    api_.short_description = _("API Status")

    def theme_(self, instance):
        return settings.THEME
    theme_.short_description = _("Theme")

    def secure_ssl_(self, instance):
        if settings.SECURE_SSL:
            return _("Enabled")
        else:
            return _("Disabled")
    secure_ssl_.short_description = _("Secure SSL")

    def debug_(self, instance):
        if settings.DEBUG:
            return _("Enabled")
        else:
            return _("Disabled")
    debug_.short_description = _("Debug")

    def static_url_(self, instance):
        return settings.STATIC_URL
    static_url_.short_description = _("Static URL")

    def static_root_(self, instance):
        return settings.STATIC_ROOT
    static_root_.short_description = _("Static Root")

    def resources_url_(self, instance):
        return settings.MEDIA_URL
    resources_url_.short_description = _("Resources URL")

    def resources_root_(self, instance):
        return settings.MEDIA_ROOT
    resources_root_.short_description = _("Resources Root")

    def upload_root_(self, instance):
        return settings.UPLOAD_ROOT
    upload_root_.short_description = _("Upload Root")

    form = SettingForm
    readonly_fields = [
        'debug_',
        'site_',
        'secure_ssl_',
        'redis_',
        'memcached_',
        'api_',
        'memcached_interval_',
        'theme_',
        'static_url_',
        'static_root_',
        'resources_url_',
        'resources_root_',
        'upload_root_',
    ]
    fieldsets = [
        (_('General'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['debug_', 'secure_ssl_', 'site_', 'active_release']
        }),
        (_('Packages List'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['enable_pdiffs', 'packages_compression',
                       'packages_validation', 'downgrade_support']
        }),
        # Frontend
        (_('Theme'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['theme_'],
            'description': '<div class="help">DCRM/settings.py</div>'
        }),
        (_('Display'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['favicon', 'advanced_mode', 'version_history', 'enable_comments',
                       'show_notice', 'notice', 'show_advertisement', 'advertisement']
        }),
        (_('Social'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['display_social', 'qq_group_name', 'qq_group_url',
                       'weibo_name', 'weibo_url',  'telegram_name', 'telegram_url', 'alipay_url',
                       'twitter_name', 'twitter_url', 'facebook_name', 'facebook_url', 'paypal_url']
        }),
        (_('Statistics'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['external_statistics', 'internal_statistics']
        }),
        (_('Footer'), {
            'classes': ('suit-tab suit-tab-frontend',),
            'fields': ['copyright_name', 'copyright_year',
                       'footer_icp']
        }),
        # Security
        (_('Security'), {
            'classes': ('suit-tab suit-tab-security',),
            'fields': ['gpg_signature', 'gpg_password']
        }),
        # Advanced
        (_('API'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['api_'],
            'description': '<div class="help">DCRM/settings.py</div>'
        }),
        (_('Cache'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['memcached_', 'memcached_interval_'],
            'description': '<div class="help">DCRM/settings.py</div>'
        }),
        (_('Queue'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['redis_'],
            'description': '<div class="help">DCRM/settings.py</div>'
        }),
        (_('Static'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['static_url_', 'static_root_'],
            'description': '<div class="help">DCRM/settings.py</div>'
        }),
        (_('Upload'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['upload_root_'],
            'description': '<div class="help">DCRM/settings.py</div>'
        }),
        (_('Resource'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['atomic_storage', 'resources_url_', 'resources_root_', 'resources_alias']
        }),
        (_('Server'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['download_count', 'download_cydia_only', 'redirect_resources', 'redirect_prefix', 'web_server'],
            'description': _("This section only works when \"Download Count\" is enabled.")
        }),
        # Third Party
    ]

    suit_form_tabs = (
        ('common', _('Common')),
        ('frontend', _('Frontend')),
        ('advanced', _('Advanced')),
        ('security', _('Security')),
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
