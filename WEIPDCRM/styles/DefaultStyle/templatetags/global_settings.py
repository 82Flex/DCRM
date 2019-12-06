# coding=utf-8

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

from django import template
from preferences import preferences
from django.contrib.sites.models import Site
from django.conf import settings
from DCRM.settings import LANGUAGE_CODE
register = template.Library()

rtl_support = ['ar']


@register.simple_tag(takes_context=True)
def global_settings(context):
    context['settings'] = preferences.Setting
    current_site = Site.objects.get(id=settings.SITE_ID)
    context['site'] = current_site.domain
    context['rtl_support'] = LANGUAGE_CODE in rtl_support
    return ''
