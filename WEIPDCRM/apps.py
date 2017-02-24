# coding:utf-8

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
