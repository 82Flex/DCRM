# coding:utf-8

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

from __future__ import unicode_literals
from django.apps import AppConfig
from suit.apps import DjangoSuitConfig
from suit.menu import ParentItem, ChildItem


class WeipdcrmConfig(AppConfig):
    name = "WEIPDCRM"
    verbose_name = 'WEIPDCRM'


class SuitConfig(DjangoSuitConfig):
    verbose_name = "WEIPDCRM"
    menu = (
        ParentItem('Sites', children=[
            ChildItem(model='sites.site'),
            ChildItem('Django RQ', url='/admin/sites/django-rq/'),
        ]),
        ParentItem('Authentication and Authorization', children=[
            ChildItem(model='auth.user'),
            ChildItem(model='auth.group'),
        ]),
        ParentItem('WEIPDCRM', children=[
            ChildItem(model='WEIPDCRM.package'),
            ChildItem(model='WEIPDCRM.version'),
            ChildItem(model='WEIPDCRM.section'),
            ChildItem(model='WEIPDCRM.release'),
            ChildItem(model='WEIPDCRM.build'),
            ChildItem(model='WEIPDCRM.osversion'),
            ChildItem(model='WEIPDCRM.devicetype'),
            ChildItem(model='WEIPDCRM.setting'),
        ]),
        ParentItem('Upload', children=[
            ChildItem('New Package', url='/admin/upload/'),
        ], align_right=True),
        ParentItem('Help', children=[
            ChildItem('Statistics', url='/admin/help/statistics/'),
            ChildItem('About...', url='/admin/help/about/'),
        ], align_right=True),
    )
