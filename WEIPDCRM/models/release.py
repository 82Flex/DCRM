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
from django.utils.translation import ugettext as _
from django.core.validators import validate_slug, FileExtensionValidator

from preferences import preferences


class Release(models.Model):
    """
    DCRM Base Model: Release
    This model manages releases (repository control info),
    and all package list builds will be assigned to one of
    these instances.
    """

    class Meta(object):
        verbose_name = _("Release")
        verbose_name_plural = _("Releases")

    # Base Property
    id = models.AutoField(primary_key=True, editable=False)
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True
    )

    origin = models.CharField(
        verbose_name=_("Origin"),
        max_length=255,
        help_text=_("This is used by Cydia as the name of the repository as shown in the "
                    "source editor (and elsewhere). This should be a longer, but not insanely "
                    "long, description of the repository."),
        default=""
    )

    label = models.CharField(
        verbose_name=_("Label"),
        max_length=255,
        help_text=_("On the package list screens, Cydia shows what repository and section "
                    "packages came from. This location doesn't have much room, though, so "
                    "this field should contain a shorter/simpler version of the name of the "
                    "repository that can be used as a tag."),
        default=""
    )

    suite = models.CharField(
        verbose_name=_("Suite"),
        max_length=255,
        help_text=_("Just set this to \"stable\". This field might not be required, but who "
                    "really knows? I, for certain, do not."),
        default=_("stable"),
        blank=True,
        validators=[
            validate_slug
        ]
    )

    version = models.CharField(
        verbose_name=_("Version"),
        max_length=255,
        help_text=_("This is an arbitrary version number that nothing actually parses. "
                    "I am going to look into seeing how required it is."),
        default=_("0.0.1-1"),
    )

    codename = models.CharField(
        verbose_name=_("Codename"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("In an \"automatic\" repository you might store multiple distributions "
                    "of software for different target systems. For example: apt.saurik.com's "
                    "main repository houses content both for desktop Debian Etch systems as "
                    "well as the iPhone. This codename then describes what distribution we "
                    "are currently looking for.")
    )

    architectures = models.CharField(
        verbose_name=_("Architectures"),
        max_length=255,
        help_text=_("To verify a repository is for the specific device you are working with "
                    "APT looks in the release file for this list. You must specify all of the "
                    "architectures that appear in your Packages file here. Again, we use "
                    "darwin-arm for 1.1.x and iphoneos-arm for 2.x."),
        default=_("iphoneos-arm"),
        blank=True
    )

    components = models.CharField(
        verbose_name=_("Components"),
        max_length=255,
        help_text=_("Just set this to \"main\". This field might not be required, but who "
                    "really knows? I, for certain, do not."),
        default=_("main"),
        blank=True,
        validators=[
            validate_slug
        ]
    )

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        help_text=_("On the package source screen a short description is listed of the repository. "
                    "This description may eventually work similarly to that of a package (with a "
                    "long/short variety and the aforementioned encoding), but for right now only "
                    "the shorter description is displayed directly on the list.")
    )

    keywords = models.CharField(
        verbose_name=_("Keywords"),
        max_length=255,
        help_text=_("Separated by commas."),
        default="",
        blank=True
    )

    # Warning: this field will store icon/file relative to MEDIA_URL,
    #          defined in settings.py.
    icon = models.FileField(
        verbose_name=_("Repository Icon"),
        max_length=255,
        upload_to="repository-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['png'])
        ]
    )

    support = models.URLField(
        verbose_name=_("Support"),
        max_length=255,
        help_text=_("Official site to provide support."),
        blank=True,
        null=True
    )

    email = models.EmailField(
        verbose_name=_("E-mail"),
        max_length=255,
        help_text=_("Maintainer's E-mail to provide support."),
        blank=True,
        null=True
    )

    def __str__(self):
        return self.label + " (" + self.origin + ")"

    @staticmethod
    def get_change_list_url():
        """
        :return: URL String
        :rtype: str
        """
        content_type = ContentType.objects.get_for_model(Release)
        return urlresolvers.reverse(
            "admin:%s_%s_changelist" % (content_type.app_label, content_type.model)
        )
    
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
    
    def get_control_field(self):
        # original
        """
        Generate control dictionary from instance properties

        :rtype: dict
        :return: No return value
        """
        """
        Standard Keys
        """
        control_field = {
            "Origin": self.origin,
            "Label": self.label,
            "Suite": self.suite,
            "Version": self.version,
            "Codename": self.codename,
            "Architectures": self.architectures,
            "Components": self.components,
            "Description": self.description,
            "Support": self.support,
        }
        control = {}
        for (k, v) in control_field.items():
            if v is not None and len(str(v)) > 0:
                control[k] = str(v)
        return control


@receiver(models.signals.post_delete, sender=Release)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    :type instance: Release
    """
    if instance.icon.name is not None:
        actual_path = os.path.join(settings.MEDIA_ROOT, instance.icon.name[1:])
        if os.path.isfile(actual_path):
            os.unlink(actual_path)
