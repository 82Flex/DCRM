# coding:utf-8
"""
Class Implementation: Device Type
"""

from __future__ import unicode_literals

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.core.validators import validate_slug


class DeviceType(models.Model):
    """
    For DCRM Compatibility Module
    """
    class Meta(object):
        verbose_name = _("Device Type")
        verbose_name_plural = _("Device Types")

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
        validators=[
            validate_slug
        ]
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

    def __unicode__(self):
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
