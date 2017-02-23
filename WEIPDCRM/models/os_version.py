# coding:utf-8
"""
Class Implementation: OS Version
"""

from __future__ import unicode_literals

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.core.validators import validate_slug


class OSVersion(models.Model):
    """
    For DCRM Compatibility Module
    """
    class Meta(object):
        verbose_name = _("iOS Version")
        verbose_name_plural = _("iOS Versions")

    # Base Property
    id = models.AutoField(primary_key=True, editable=False)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True)
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
        help_text=_("Example: 14C92/11A466"),
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        upload_to="os-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True
    )

    def __unicode__(self):
        return self.descriptor + " (" + self.build + ")"

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
