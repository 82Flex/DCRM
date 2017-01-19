# coding:utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _


class DeviceType(models.Model):
    class Meta:
        verbose_name = _("Device Type")
        verbose_name_plural = _("Device Types")

    # Base Property
    id = models.IntegerField(primary_key=True, editable=False)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
    )
    descriptor = models.CharField(
        verbose_name=_("Descriptor"),
        max_length=255,
        help_text=_("Example: iPhone 7 Plus")
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
    icon = models.ImageField(
        verbose_name=_("Icon"),
        upload_to="device-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True
    )

    def __str__(self):
        return self.descriptor + " (" + self.subtype + ")"
