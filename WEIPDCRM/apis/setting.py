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

from rest_framework import serializers, viewsets, permissions
from WEIPDCRM.apis.release import ReleaseSerializer
from WEIPDCRM.apis.site import SiteSerializer
from WEIPDCRM.models.setting import Setting
from WEIPDCRM.permissions import DenyAny


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        exclude = []

    _favicon_link = serializers.URLField(source='favicon_link', read_only=True)
    _active_release = ReleaseSerializer(source='active_release', many=False, read_only=True)
    sites = SiteSerializer(many=True, read_only=True)


class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == 'partial_update' or self.action == 'update':
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [DenyAny]
        return [permission() for permission in permission_classes]
