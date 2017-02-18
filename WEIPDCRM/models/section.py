# coding:utf-8
"""
DCRM Section Module
"""

from __future__ import unicode_literals

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug


def validator_underscore(value):
    """
    :param value: Input Value
    :type value: str
    """
    if '_' in value:
        raise ValidationError(_("Section name should not contain any underscore."))


class Section(models.Model):
    """
    DCRM Base Model: Section
    """
    class Meta(object):
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    # Base Property
    id = models.AutoField(primary_key=True, editable=False)
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True, editable=False)
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("This is a general field that gives the package a category "
                    "based on the software that it installs. You will not "
                    "be able to edit its name after assigning any package under it."),
        unique=True,
        validators=[
            validate_slug,
            validator_underscore
        ]
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        upload_to="section-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True,
        null=True
    )

    def __unicode__(self):
        return self.name

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
