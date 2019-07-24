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

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, viewsets, permissions
from rest_framework.pagination import LimitOffsetPagination
from WEIPDCRM.apis.section import SectionSerializer
from WEIPDCRM.apis.version import VersionSerializer
from WEIPDCRM.models.package import Package
from WEIPDCRM.permissions import DenyAny


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

    _absolute_url = serializers.URLField(source='get_absolute_url', read_only=True)
    _display_icon = serializers.URLField(source='display_icon', read_only=True)
    _latest_version = VersionSerializer(source='get_latest_version', many=False, read_only=True)

    _c_section = SectionSerializer(source='c_section', many=False, read_only=True)


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['c_package', 'c_section']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [DenyAny]
        return [permission() for permission in permission_classes]
