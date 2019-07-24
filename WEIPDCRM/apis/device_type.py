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
from rest_framework import serializers, viewsets
from WEIPDCRM.models.device_type import DeviceType


class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'


class DeviceTypeViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceTypeSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['enabled', 'platform', 'subtype']

    def get_queryset(self):
        queryset = DeviceType.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(enabled=True)
        return queryset
