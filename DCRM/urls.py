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

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from WEIPDCRM.api import get_router
from WEIPDCRM.views import publish
from WEIPDCRM.views.admin import release
from WEIPDCRM.views.admin import upload
from WEIPDCRM.views.admin.help import about
from WEIPDCRM.views.admin.help import statistics

theme_module = settings.THEME

urlpatterns = [
    # Notice: Good Bro! Use 'include' to import urls from other apps.
    url(r'^', include('WEIPDCRM.styles.' + theme_module + '.urls')),
    url(r'^comments/', include('fluent_comments.urls')),
    
    # Basic List
    url(
        r'^(?P<resource_name>(CydiaIcon(.png)?|Release(.gpg)?|Packages(.gz|.bz2)?))$',
        publish.basic_resource_fetch,
        name='basic_resource_fetch'
    ),
    url(
        r'^debs/(?P<package_id>\d+)\.deb$',
        publish.package_file_fetch,
        name='package_file_fetch'
    ),
    url(
        r'^debs/(?P<package_name>.+?)/(?P<package_id>(\d+|latest))\.deb$',
        publish.package_file_fetch,
        name='package_file_fetch_with_name'
    ),
    
    # Admin Panel
    url(r'^admin/', admin.site.urls),
    url(r'^admin/upload/$', upload.upload_view, name='upload'),
    url(r'^admin/upload/version/$', upload.upload_version_view, name='version_add'),
    url(r'^admin/upload/screenshots/(?P<package_id>\d+)/(?P<gallery_slug>[0-9A-Za-z|_\-]+)/?$', upload.upload_screenshots_view, name='screenshots_add'),
    url(r'^admin/release/set-default/(?P<release_id>\d+)/?$', release.set_default_view, name='set_default_release'),
    url(r'^admin/help/about/$', about.about_view, name='help_about'),
    url(r'^admin/help/statistics/$', statistics.statistics_view, name='help_statistics'),

    # Photologue
    url(r'^photologue/', include('photologue.urls', namespace='photologue'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.ENABLE_REDIS is True:
    urlpatterns.append(url(r'^admin/sites/django-rq/', include('django_rq.urls')))

if settings.ENABLE_API is True:
    urlpatterns += [
        url(r'^api/', include(get_router().urls)),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]


handler400 = 'WEIPDCRM.views.error.bad_request'
handler404 = 'WEIPDCRM.views.error.page_not_found'
handler500 = 'WEIPDCRM.views.error.server_error'
