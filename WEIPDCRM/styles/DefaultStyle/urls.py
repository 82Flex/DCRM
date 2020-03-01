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

from django.conf.urls import url

from .views.index import IndexView
from .views.package import PackageView
from .views.section import SectionView
from .views.search import search_view
from .views.chart import ChartView
from .views.section_list import SectionListView

from django.views.decorators.cache import cache_page
from django.conf import settings


def cache():
    return cache_page(getattr(settings, 'CACHE_TIME', 0)) \
        if getattr(settings, 'ENABLE_CACHE', False) else lambda x: x

urlpatterns = [
    url(r'^$', cache()(IndexView.as_view()), name='index'),
    url(r'^index/(?P<page>\d*)/?$', cache()(IndexView.as_view()), name='index_page'),
    url(r'^package/(?P<package_id>\d+)/?$', cache()(PackageView.as_view()), name='package_id'),
    url(r'^package/(?P<package_id>\d+)/(?P<action_name>[0-9A-Za-z]+)/?$', cache()(PackageView.as_view()), name='package_action'),
    url(r'^search/?$', cache()(search_view), name='search'),
    url(r'^chart/?$', cache()(ChartView.as_view()), name='chart'),
    url(r'^section/list/?$', cache()(SectionListView.as_view()), name='section_list'),
    url(r'^section/list/(?P<page>\d*)/?$', cache()(SectionListView.as_view()), name='section_list_page'),
    url(r'^section/(?P<section_id>\d+)/?$', cache()(SectionView.as_view()), name='section_id'),
    url(r'^section/(?P<section_id>\d+)/(?P<page>\d*)/?$', cache()(SectionView.as_view()), name='section_id_page'),
]
