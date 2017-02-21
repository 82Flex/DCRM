# coding=utf-8

"""
DCRM Proxy Package Module
This is a proxy object of Version, it will not generate a table in database.
It just groups all versions in the same package, and list the latest version of that package.
"""

from __future__ import unicode_literals

from django.db import models
from WEIPDCRM.models.version import Version
from django.utils.translation import ugettext as _


class PackageManager(models.Manager):
    def get_queryset(self):
        # TODO: Edit this query to make sure no duplicate package in the change list
        query_set = super(PackageManager, self).get_queryset()
        return query_set


class Package(Version):
    """
    DCRM Proxy Model: Package
    """

    class Meta(object):
        proxy = True
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")

    objects = PackageManager()
