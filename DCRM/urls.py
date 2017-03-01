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

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from WEIPDCRM.views.admin import upload
from WEIPDCRM.views.admin.help import about
from WEIPDCRM.views.admin.help import statistics
from WEIPDCRM.views.admin import release

urlpatterns = [
    # Notice: Good Bro! Use 'include' to import urls from other apps.
    url(r'^', include('WEIPDCRM.styles.DefaultStyle.urls')),
    
    # Admin Panel
    url(r'^admin/', admin.site.urls),
    url(r'^admin/sites/django-rq/', include('django_rq.urls')),
    url(r'^admin/upload/$', upload.upload_view, name='upload'),
    url(r'^admin/upload/version/$', upload.upload_version_view, name='version_add'),
    url(r'^admin/release/set-default/(?P<release_id>\d+)$', release.set_default_view, name='set_default_release'),
    url(r'^admin/help/about/$', about.about_view, name='help_about'),
    url(r'^admin/help/statistics/$', statistics.statistics_view, name='help_statistics'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
