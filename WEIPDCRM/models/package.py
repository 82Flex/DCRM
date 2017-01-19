# coding:utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _
from WEIPDCRM.models.section import Section


class Package(models.Model):
    class Meta:
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")

    # Base Property
    id = models.IntegerField(
        primary_key=True,
        editable=False
    )
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        upload_to="package-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True
    )

    # Controls
    package = models.CharField(
        verbose_name=_("Package"),
        max_length=255,
        help_text=_("Unique identifier. "
                    "The value of this field determines the package name, "
                    "and is used to generate file names by most installation tools.<br />"
                    "Example: com.darwindev.xxtouch"),
        unique=True
    )
    section = models.ForeignKey(Section)
    author_name = models.CharField(
        verbose_name=_("Author"),
        max_length=255
    )
    author_email = models.EmailField(
        verbose_name=_("Author Email"),
        max_length=255,
        blank=True
    )
    maintainer_name = models.CharField(
        verbose_name=_("Maintainer"),
        max_length=255,
        help_text=_("It is typically the person who created the package, as opposed to "
                    "the author of the software that was packaged.")
    )
    maintainer_email = models.EmailField(
        verbose_name=_("Maintainer Email"),
        max_length=255,
        blank=True
    )
    sponsor_name = models.CharField(
        verbose_name=_("Sponsor"),
        max_length=255
    )
    sponsor_email = models.EmailField(
        verbose_name=_("Sponsor Email"),
        max_length=255,
        blank=True
    )
    depiction = models.URLField(
        blank=True,
        help_text=_("Detail page related to this package."),
        default=""
    )
    homepage = models.URLField(
        blank=True,
        default=""
    )
    description = models.TextField(
        blank=True,
        help_text=_("The format for the package description is a short brief "
                    "summary on the first line (after the Description field). The "
                    "following lines should be used as a longer, more detailed "
                    "description."),
        default=""
    )

    def __str__(self):
        return self.name
