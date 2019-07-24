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

from __future__ import unicode_literals

import uuid

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from WEIPDCRM.models.release import Release


class Build(models.Model):
    """
    DCRM Base Model: Build
    Build model manages package builds history like
     - Packages (Plain Text)
     - Packages Compressions (gz, bz2, lzma, xz)
     - Packages Diff (PDiff Feature)
    Each valid Build instance is under an active release.
    You can only create or delete builds, and you cannot edit them.
    """
    
    class Meta(object):
        verbose_name = _("Build")
        verbose_name_plural = _("Builds")
        ordering = ("-created_at", )

    # Base Property
    uuid = models.UUIDField(
        verbose_name=_("UUID"),
        primary_key=True,
        default=uuid.uuid4
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True
    )
    active_release = models.ForeignKey(
        Release,
        verbose_name=_("Active Release"),
        on_delete=models.CASCADE,
        blank=False,
        null=None,
    )
    job_id = models.CharField(
        verbose_name=_("Job ID"),
        max_length=64,
        blank=False,
        null=True,
        default=None
    )
    is_finished = models.BooleanField(
        verbose_name=_("Job Finished"),
        default=False
    )
    
    # History Settings
    details = models.TextField(
        verbose_name=_("Details"),
        blank=True,
        null=True,
        help_text=_("Tell others what did you do this time "
                    "before you rebuild the repository."),
        default="Fast Build"
    )
    
    def __str__(self):
        return str(self.uuid)

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

    # TODO: post delete should remove build directory
