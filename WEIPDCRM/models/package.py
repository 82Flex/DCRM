# coding=utf-8

"""
DCRM Proxy Package Module
This is a proxy object of Version, it will not generate a table in database.
It just groups all versions in the same package, and list the latest version of that package.
"""

from __future__ import unicode_literals

from django.db import models
from django.db.models import Count
from WEIPDCRM.models.version import Version
from django.utils.translation import ugettext as _


class PackageManager(models.Manager):
    def get_queryset(self):
        return super(PackageManager, self).get_queryset().annotate(version_count=Count('package'))


class Package(Version):
    """
    DCRM Proxy Model: Package
    """

    class Meta(object):
        proxy = True
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")

    objects = PackageManager()
