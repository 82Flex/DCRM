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

from __future__ import unicode_literals

from django.contrib.admin.views.decorators import staff_member_required

from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from WEIPDCRM.models.release import Release
from WEIPDCRM.models.setting import Setting


@staff_member_required
def set_default_view(request, release_id):
    """
    :param release_id: The release
    :param request: Django Request
    :return: Redirect Response
    """
    release_instance = Release.objects.get(id=release_id)
    
    messages.info(request, mark_safe(_(
        "Active release \"<a href=\"{release_url}\">{release}</a>\" has been set.").format(
            release_url=release_instance.get_admin_url(),
            release=str(release_instance)
        )
    ))
    
    setting_instance = Setting.objects.get()
    setting_instance.active_release = release_instance
    setting_instance.save()
    
    return redirect(setting_instance.get_admin_url())
