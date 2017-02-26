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

DCRM Proxy Package Module
This is a proxy object of Version, it will not generate a table in database.
It just groups all versions in the same package, and list the latest version of that package.
"""

from __future__ import unicode_literals

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from WEIPDCRM.models.version import Version
from WEIPDCRM.models.section import Section


class Package(models.Model):
    """
    DCRM Proxy Model: Package
    """

    class Meta(object):
        """
        Using Database VIEW to make it.
        This is an unmanaged model, and `package_view` is actually a Database VIEW.
        Its creating query which select only useful fields and latest version below from each package.
        """
        managed = False
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")
        db_table = "package_view"
    
    c_name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At")
    )
    c_package = models.CharField(
        verbose_name=_("Package"),
        max_length=255,
    )
    c_version = models.CharField(
        verbose_name=_("Version"),
        max_length=255
    )
    c_section = models.ForeignKey(
        Section,
        verbose_name=_("Section")
    )
    
    def get_version_admin_url(self):
        """
        :return: URL String
        :rtype: str
        """
        content_type = ContentType.objects.get_for_model(Version)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, "version"),
            args=(self.id,)
        )
