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

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers, permissions
from rest_framework.permissions import BasePermission

from WEIPDCRM.models.build import Build
from WEIPDCRM.models.device_type import DeviceType
from WEIPDCRM.models.os_version import OSVersion
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.release import Release
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.setting import Setting
from WEIPDCRM.models.version import Version


class DenyAny(BasePermission):
    def has_permission(self, request, view):
        return False


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'url', 'username', 'first_name', 'last_name',
            'email', 'is_active', 'is_staff', 'is_superuser',
            'last_login', 'date_joined'
        ]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [DenyAny]
        return [permission() for permission in permission_classes]


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = [
            'url', 'id', 'origin', 'label',
            'version', 'codename', 'icon', 'description',
            'suite', 'components', "support", "email",
            'keywords', 'created_at']


class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = [
            'url', 'id', 'name', 'icon', 'created_at']


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            'url', 'id', 'c_package', 'c_version',
            'c_name', 'c_section']


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [DenyAny]
        return [permission() for permission in permission_classes]


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = [
            'url', 'id', 'enabled',
            'c_package', 'c_version', 'c_name',
            'c_section', 'c_icon', 'online_icon',
            'c_description', 'update_logs',
            'custom_depiction', 'c_depiction', 'c_homepage',
            'rich_description', 'os_compatibility', 'device_compatibility',
            'maintainer_name', 'maintainer_email',
            'author_name', 'author_email',
            'sponsor_name', 'sponsor_site',
            'c_architecture', 'c_priority', 'c_essential', 'c_tag',
            'c_depends', 'c_pre_depends', 'c_conflicts', 'c_replaces', 'c_provides',
            'c_recommends', 'c_suggests', 'c_breaks',
            'storage_link', 'c_size', 'c_installed_size',
            'c_md5', 'c_sha1', 'c_sha256', 'c_sha512',
            'c_origin', 'c_source', 'c_bugs', 'c_installer_menu_item',
            'c_build_essential', 'c_built_using', 'c_built_for_profiles',
            'c_multi_arch', 'c_subarchitecture', 'c_kernel_version',
            'download_times', 'created_at',
            # 'gallery',
        ]
        # TODO: add depiction url, icon url, absolute url, download_url


class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer

    # TODO: allow version changes (too complicated without panel)
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [DenyAny]
        return [permission() for permission in permission_classes]


class BuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Build
        fields = [
            'url', 'uuid', 'active_release', 'job_id',
            'details', 'created_at',
        ]


class BuildViewSet(viewsets.ModelViewSet):
    queryset = Build.objects.all()
    serializer_class = BuildSerializer

    # TODO: allow build changes (create only)
    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [DenyAny]
        return [permission() for permission in permission_classes]


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = [
            'url', 'enabled', 'descriptor', 'subtype',
            'platform', 'icon', 'created_at'
        ]


class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer


class OSVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OSVersion
        fields = [
            'url', 'enabled', 'descriptor', 'build',
            'icon', 'created_at'
        ]


class OSVersionViewSet(viewsets.ModelViewSet):
    queryset = OSVersion.objects.all()
    serializer_class = OSVersionSerializer


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = [
            'url', 'active_release', 'enable_pdiffs', 'gpg_signature',
            'packages_compression', 'packages_validation', 'downgrade_support',
            'advanced_mode', 'version_history', 'enable_comments', 'favicon',
            'notice', 'advertisement', 'display_social', 'qq_group_name', 'qq_group_url',
            'weibo_name', 'weibo_url', 'telegram_name', 'telegram_url', 'alipay_url',
            'twitter_name', 'twitter_url', 'facebook_name', 'facebook_url', 'paypal_url',
            'external_statistics', 'internal_statistics',
            'copyright_name', 'copyright_year', 'footer_icp',
            'atomic_storage', 'resources_alias',
            'web_server', 'redirect_resources', 'redirect_prefix',
            'download_count', 'download_cydia_only', 'rest_api'
        ]


class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [DenyAny]
        return [permission() for permission in permission_classes]


def get_router():
    router = routers.DefaultRouter()
    router.register(r'users', UserViewSet)
    router.register(r'releases', ReleaseViewSet)
    router.register(r'sections', SectionViewSet)
    router.register(r'packages', PackageViewSet)
    router.register(r'versions', VersionViewSet)
    router.register(r'builds', BuildViewSet)
    router.register(r'device_types', DeviceTypeViewSet)
    router.register(r'os_versions', OSVersionViewSet)
    router.register(r'settings', SettingViewSet)
    return router
