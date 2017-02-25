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

import re
from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from preferences.models import Preferences

from WEIPDCRM.models.release import Release


def validator_basic(value):
    """
    :param value: Input Value
    :type value: str
    """
    pattern = re.compile(r"^[0-9A-Za-z_.\-/]+$")
    if not pattern.match(value):
        raise ValidationError(_("Only these characters are allowed: 0-9A-Za-z_.-/"))


def validate_alias(value):
    """
    :param value: Input Value
    :type value: str
    """
    if value[len(value) - 1:] != '/':
        raise ValidationError(_("Path alias should be suffixed by a slash char."))


class Setting(Preferences):
    """
    DCRM Base Model: Setting
    This is a single instance, just for global settings.
    
    Normally, it will has only one instance with primary key id=1,
    and it will be assigned to a specific site instance. You should
    not delete the site and this instance.
    """
    class Meta(object):
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")
    active_release = models.ForeignKey(
        Release,
        verbose_name=_("Active Release"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Each repository should have an active release, otherwise it will not be "
                    "recognized by any advanced package tools.")
    )
    packages_compression = models.IntegerField(
        verbose_name=_("Packages Compression"),
        choices=(
            (0, _("Plain")),
            (1, _("Gzip")),
            (2, _("Plain and Gzip")),
            (3, _("Bzip")),
            (4, _("Plain and Bzip")),
            (5, _("Gzip and Bzip")),
            (6, _("All (Recommended)")),
        ),
        default=6,
        help_text=_(
            "Please change the compression method if error occurred when try to rebuild the list."
        )
    )
    packages_validation = models.IntegerField(
        verbose_name=_("Packages Validation"),
        choices=(
            (0, _("No validation")),
            (1, _("MD5Sum")),
            (2, _("MD5Sum & SHA1")),
            (3, _("MD5Sum & SHA1 & SHA256 (Recommended)")),
            (4, _("MD5Sum & SHA1 & SHA256 & SHA512")),
        ),
        default=3,
        help_text=_(
            "You need to update hashes manually."
        ),
    )
    downgrade_support = models.BooleanField(
        verbose_name=_("Downgrade Support"),
        help_text=_(
            "Allow multiple versions to exist in the latest package list."
        ),
        default=True
    )
    advanced_mode = models.BooleanField(
        verbose_name=_("Auto Depiction"),
        help_text=_(
            "Check it to generate awesome depiction page for each version."
        ),
        default=True
    )
    atomic_storage = models.BooleanField(
        verbose_name=_("Atomic Storage"),
        help_text=_(
            "Generate a new copy of package after editing control columns."
        ),
        default=False
    )
    resources_alias = models.CharField(
        verbose_name=_("Resources Alias"),
        help_text=_("You can specify alias for resources path in Nginx or "
                    "other HTTP servers, which is necessary for CDN speedup."),
        max_length=255,
        default="/resources/",
        validators=[
            validator_basic,
            validate_alias
        ]
    )
    enable_pdiffs = models.BooleanField(
        verbose_name=_("Enable pdiffs"),
        help_text=_("If package list is extremely large, you should enable this to allow incremental update."),
        default=False
    )
    rest_api = models.BooleanField(
        verbose_name=_("Enable Rest API"),
        help_text=_("Upload packages using HTTP, manage your repositories, snapshots, published repositories etc."),
        default=False
    )

    def get_admin_url(self):
        """
        :return: URL String
        :rtype: str
        """
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(self.id,)
        )
