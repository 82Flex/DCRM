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
        query_list = super(PackageManager, self).get_queryset().raw(
            "SELECT t1.* "
            "FROM `%s` t1 "
            "LEFT JOIN `%s` t2 "
            "ON (t1.`package` = t2.`package` AND t1.`id` < t2.`id`) "
            "WHERE t2.`id` IS NULL AND t1.`enabled` = TRUE" %
            (Version._meta.db_table, Version._meta.db_table)
        )
        id_list = []
        for query_t in query_list:
            id_list.append(query_t.id)
        query_set = super(PackageManager, self).get_queryset().filter(id__in=id_list)
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
