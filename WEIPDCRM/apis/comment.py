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
from rest_framework import serializers, viewsets, routers, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission
from threadedcomments.models import ThreadedComment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadedComment
        exclude = ['site', 'user']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = ThreadedComment.objects.all()
    # permission_classes = [AllowAny]
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'object_pk',
                        'user_name', 'user_email',
                        'is_public', 'is_removed',
                        'parent', 'last_child']
