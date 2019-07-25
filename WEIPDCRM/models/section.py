# coding:utf-8

"""
DCRM - Darwin Cydia Repository Manager
Copyright (C) 2017  WU Zheng <i.82@me.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug

from preferences import preferences


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
    This model manages all sections, which is important in Cydia interface.
    
    But you cannot edit its name due to the duplicated section field in .deb
    control part, if you force DCRM to change the section name, DCRM has to
    generate all .deb files and calculate their hashes under this section again,
    which may causes huge cost. So you should create some Sections first, and
    then assign versions to them.
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
            validator_underscore
        ]
    )

    # Warning: this field will store icon/file relative to MEDIA_URL,
    #          defined in settings.py.
    icon = models.FileField(
        verbose_name=_("Icon"),
        max_length=255,
        upload_to="section-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True,
        null=True,
    )

    def __str__(self):
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

    def get_external_icon_link(self):
        """
        This getter method for icon_link property generates outer
        link for frontend icon display.

        :return: External Icon Link
         :rtype: str
        """
        if not self.icon:
            return None
        file_path = self.icon.name
        return str(preferences.Setting.resources_alias) + file_path

    icon_link = property(get_external_icon_link)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('section_id', args=[self.id])


@receiver(models.signals.post_delete, sender=Section)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    :type instance: Section
    """
    if instance.icon.name is not None:
        actual_path = os.path.join(settings.MEDIA_ROOT, instance.icon.name[1:])
        if os.path.isfile(actual_path):
            os.unlink(actual_path)
