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

from rest_framework import routers

from WEIPDCRM.apis.build import BuildViewSet
from WEIPDCRM.apis.comment import CommentViewSet
from WEIPDCRM.apis.contenttype import ContentTypeViewSet
from WEIPDCRM.apis.device_type import DeviceTypeViewSet
from WEIPDCRM.apis.group import GroupViewSet
from WEIPDCRM.apis.os_version import OSVersionViewSet
from WEIPDCRM.apis.package import PackageViewSet
from WEIPDCRM.apis.permission import PermissionViewSet
from WEIPDCRM.apis.release import ReleaseViewSet
from WEIPDCRM.apis.section import SectionViewSet
from WEIPDCRM.apis.setting import SettingViewSet
from WEIPDCRM.apis.site import SiteViewSet
from WEIPDCRM.apis.user import UserViewSet
from WEIPDCRM.apis.version import VersionViewSet
from WEIPDCRM.apis.gallery import GalleryViewSet
from WEIPDCRM.apis.photo import PhotoViewSet


def get_router():
    router = routers.DefaultRouter()
    router.register(r'contenttypes', ContentTypeViewSet, 'contenttype')
    router.register(r'groups', GroupViewSet, 'group')
    router.register(r'users', UserViewSet, 'user')
    router.register(r'permissions', PermissionViewSet, 'permission')
    router.register(r'releases', ReleaseViewSet, 'release')
    router.register(r'sections', SectionViewSet, 'section')
    router.register(r'packages', PackageViewSet, 'package')
    router.register(r'versions', VersionViewSet, 'version')
    router.register(r'builds', BuildViewSet, 'build')
    router.register(r'device_types', DeviceTypeViewSet, 'device_type')
    router.register(r'os_versions', OSVersionViewSet, 'os_version')
    router.register(r'settings', SettingViewSet, 'setting')
    router.register(r'galleries', GalleryViewSet, 'gallery')
    router.register(r'photos', PhotoViewSet, 'photo')
    router.register(r'comments', CommentViewSet, 'comment')
    router.register(r'sites', SiteViewSet, 'site')
    return router
