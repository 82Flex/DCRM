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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

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
            ChildItem(_('Django RQ'), url='rq_home'),
            ChildItem(model='scheduler.cronjob'),
            ChildItem(model='scheduler.repeatablejob'),
            ChildItem(model='scheduler.scheduledjob'),
        ]),
        ParentItem('Authentication and Authorization', children=[
            ChildItem(model='auth.user'),
            ChildItem(model='auth.group'),
        ]),
        ParentItem('WEIPDCRM', children=[
            ChildItem(model='WEIPDCRM.release'),
            ChildItem(model='WEIPDCRM.build'),
            
            ChildItem(model='WEIPDCRM.package'),
            ChildItem(model='WEIPDCRM.version'),
            ChildItem(model='WEIPDCRM.section'),
            
            ChildItem(model='WEIPDCRM.osversion'),
            ChildItem(model='WEIPDCRM.devicetype'),
            
            ChildItem(model='WEIPDCRM.setting'),
        ]),
        ParentItem('Comments', children=[
            ChildItem(model='threadedcomments.threadedcomment'),
        ]),
        ParentItem('Photologue', children=[
            ChildItem(model='photologue.gallery'),
            ChildItem(model='photologue.photo'),
            ChildItem(model='photologue.photoeffect'),
            ChildItem(model='photologue.photosize'),
            ChildItem(model='photologue.watermark'),
        ]),
        ParentItem('Upload', children=[
            ChildItem(_('New Package'), url='upload'),
        ], align_right=True),
        ParentItem('Help', children=[
            ChildItem(_('Statistics'), url='help_statistics'),
            ChildItem(_('About...'), url='help_about'),
        ], align_right=True),
    )
