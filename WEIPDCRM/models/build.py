# coding=utf-8
"""
DCRM Build Module
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
    """
    
    class Meta(object):
        verbose_name = _("Build")
        verbose_name_plural = _("Builds")

    # Base Property
    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True
    )
    c_release = models.ForeignKey(
        Release,
        verbose_name=_("Release"),
        on_delete=models.CASCADE,
        null=True,
        editable=False
    )
    storage_package = models.FilePathField(
        verbose_name=_("Storage Package"),
        allow_files=True,
        allow_folders=False,
        max_length=255,
    )
    details = models.TextField(
        verbose_name=_("Details"),
        blank=True,
        null=True,
        editable=False,
    )
    
    def __unicode__(self):
        return self.uuid

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
