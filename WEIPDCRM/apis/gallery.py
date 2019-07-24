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
from photologue.models import Gallery
from rest_framework import serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination

from WEIPDCRM.apis.photo import PhotoSerializer


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        exclude = ['sites']

    _photos = PhotoSerializer(source='photos', many=True, read_only=True)


class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug', 'is_public']

    def get_queryset(self):
        queryset = Gallery.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_public=True)
        return queryset
