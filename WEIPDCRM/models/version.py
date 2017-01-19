# coding:utf-8

from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _
from WEIPDCRM.models.os_version import OSVersion
from WEIPDCRM.models.device_type import DeviceType
from WEIPDCRM.models.package import Package


class Version(models.Model):
    class Meta:
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")

    # Base Property
    id = models.IntegerField(primary_key=True, editable=False)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    download_times = models.IntegerField(verbose_name=_("Download Times"), default=0)

    # File System
    storage = models.FileField(
        verbose_name=_("Storage"),
        upload_to="debs",
        help_text=_("Choose a Debain Package (*.deb) to upload"),
    )
    md5 = models.CharField(verbose_name=_("MD5"), max_length=32, default="")
    sha1 = models.CharField(verbose_name=_("SHA1"), max_length=40, default="")
    sha256 = models.CharField(verbose_name=_("SHA256"), max_length=64, default="")
    size = models.BigIntegerField(verbose_name=_("Size"), default=0)

    # Controls
    package = models.ForeignKey(Package, null=False)
    version = models.CharField(
        verbose_name=_("Version"),
        max_length=255,
        help_text=_("Typically, this is the original package's version number in "
                    "whatever form the program's author uses. It may also include a "
                    "Debian revision number (for non-native packages).<br />"
                    "Example: 0.0.1-1"),
        default=_("0.0.1-1")
    )

    # Version Control
    update_logs = models.TextField(blank=True, null=True)

    # Compatibility
    os_compatibility = models.ManyToManyField(OSVersion, blank=True)
    device_compatibility = models.ManyToManyField(DeviceType, blank=True)

    # Control
    control_field = models.TextField(blank=True, null=True, editable=False)
