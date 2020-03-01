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

import os

from django.conf import settings
from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.utils.translation import ugettext as _


class DeviceType(models.Model):
    """
    For DCRM Compatibility Module
    This model manages all iOS Device Types.
    """
    class Meta(object):
        verbose_name = _("Device Type")
        verbose_name_plural = _("Device Types")
        ordering = ['-id']

    # Base Property
    id = models.AutoField(primary_key=True, editable=False)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True)
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
    )
    descriptor = models.CharField(
        verbose_name=_("Descriptor"),
        max_length=255,
        help_text=_("Example: iPhone 7 Plus"),
    )
    subtype = models.CharField(
        verbose_name=_("Subtype"),
        max_length=255,
        help_text=_("Example: iPhone9,2")
    )
    platform = models.CharField(
        verbose_name=_("Platform"),
        max_length=255,
        help_text=_("Example: A1661/A1784/A1785"),
        blank=True
    )

    # Warning: this field will store icon/file relative to MEDIA_URL,
    #          defined in settings.py.
    icon = models.FileField(
        verbose_name=_("Icon"),
        max_length=255,
        upload_to="device-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.descriptor + " (" + self.subtype + ")"

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


@receiver(models.signals.post_delete, sender=DeviceType)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    :type instance: DeviceType
    """
    if instance.icon.name is not None:
        actual_path = os.path.join(settings.MEDIA_ROOT, instance.icon.name[1:])
        if os.path.isfile(actual_path):
            os.unlink(actual_path)
