# coding:utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _


class OSVersion(models.Model):
    class Meta:
        verbose_name = _("iOS Version")
        verbose_name_plural = _("iOS Versions")

    # Base Property
    id = models.IntegerField(primary_key=True, editable=False)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
    )
    descriptor = models.CharField(
        verbose_name=_("Version"),
        max_length=255,
        help_text=_("Example: 10.2")
    )
    build = models.CharField(
        verbose_name=_("Build"),
        max_length=255,
        help_text=_("Example: 14C92")
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        upload_to="os-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True
    )

    def __str__(self):
        return self.descriptor + " (" + self.build + ")"
