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

from WEIPDCRM.styles.DefaultStyle import home
from WEIPDCRM.views.admin import upload
from WEIPDCRM.views.admin.help import about
from WEIPDCRM.views.admin.help import statistics

urlpatterns = [
    url(r'^$', home.index.as_view()),
    url(r'^page/$', home.index.as_view()),
    url(r'^package/(?P<package_id>\d+)$', home.package_view.as_view(), name='package_id'),
    #url(r'^version/(.*)', home.version_view, name='package_histroy'),
    #url(r'^section/(.*)', home.section_view, name='section_view'),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/sites/django-rq/', include('django_rq.urls')),
    url(r'^admin/upload/$', upload.upload_view, name='upload'),
    url(r'^admin/upload/version/$', upload.upload_version_view, name='version_add'),
    url(r'^admin/help/about/$', about.about_view, name='help_about'),
    url(r'^admin/help/statistics/$', statistics.statistics_view, name='help_statistics'),
]
