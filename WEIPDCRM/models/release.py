# coding:utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _


class Release(models.Model):
    class Meta:
        verbose_name = _("Release")
        verbose_name_plural = _("Releases")

    # Base Property
    id = models.IntegerField(primary_key=True, editable=False)
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True
    )

    origin = models.CharField(
        verbose_name=_("Origin"),
        max_length=255,
        help_text=_("This name will be displayed in the sources interface of Cydia."),
        default=""
    )

    label = models.CharField(
        verbose_name=_("Label"),
        max_length=255,
        help_text=_("This name will be displayed at the top of the package list interface."),
        default=""
    )

    codename = models.CharField(
        verbose_name=_("Codename"),
        max_length=255,
        default=""
    )

    keywords = models.CharField(
        verbose_name=_("Keywords"),
        max_length=255,
        help_text=_("Separated by commas."),
        default=""
    )

    description = models.TextField(blank=True)

    version = models.CharField(
        verbose_name=_("Version"),
        max_length=255,
        help_text=_("Example: 0.0.1-1"),
        default=_("0.0.1-1"),
    )

    icon = models.ImageField(
        verbose_name=_("Repository Icon"),
        upload_to="repository-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True
    )

    def __str__(self):
        return self.label + " (" + self.codename + ")"
