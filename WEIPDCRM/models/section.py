# coding:utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _


class Section(models.Model):
    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    # Base Property
    id = models.IntegerField(primary_key=True, editable=False)
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True, editable=False)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("This is a general field that gives the package a category "
                    "based on the software that it installs.")
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        upload_to="section-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True
    )

    def __str__(self):
        return self.name
