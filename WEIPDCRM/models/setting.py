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
import re
import subprocess

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, FileExtensionValidator
from django.utils.translation import ugettext_lazy as _

from WEIPDCRM.models.release import Release
from preferences import preferences
from preferences.models import Preferences


def validator_basic(value):
    """
    :param value: Input Value
    :type value: str
    """
    pattern = re.compile(r"^[0-9A-Za-z_.\-/]+$")
    if not pattern.match(value):
        raise ValidationError(_("Only these characters are allowed: 0-9A-Za-z_.-/"))


def validate_alias(value):
    """
    :param value: Input Value
    :type value: str
    """
    if value[0] != '/' or value[len(value) - 1:] != '/':
        raise ValidationError(_("Path alias should be prefixed and suffixed by slash chars."))


def validate_slash(value):
    """
        :param value: Input Value
        :type value: str
        """
    if value[len(value) - 1:] != '/':
        raise ValidationError(_("Path alias should be suffixed by a slash char."))


def validate_gpg(value):
    """
    Check if gpg command has been installed.
    """
    if value:
        try:
            subprocess.check_call(['gpg', '--homedir', os.path.join(settings.BASE_DIR, '.gnupg'), '--version', '--batch', '--yes'])
        except Exception as e:
            raise ValidationError(_("Cannot find command 'gpg': %s") % str(e))


def validate_web_server(value):
    if value != 0 and value != 1:
        raise ValidationError(_("Only Nginx/Apache are supported now."))


def validate_pdiffs(value):
    if value:
        raise ValidationError(_("pdiffs is not supported now."))


def validate_rest_api(value):
    if value:
        raise ValidationError(_("Rest API is not supported now."))


class Setting(Preferences):
    """
    DCRM Base Model: Setting
    This is a single instance, just for global settings.
    
    Normally, it will has only one instance with primary key id=1,
    and it will be assigned to a specific site instance. You should
    not delete the site and this instance.
    """
    class Meta(object):
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")
    active_release = models.ForeignKey(
        Release,
        verbose_name=_("Active Release"),
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        help_text=_("Each repository should have an active release, otherwise it will not be "
                    "recognized by any advanced package tools.")
    )

    packages_compression = models.IntegerField(
        verbose_name=_("Packages Compression"),
        choices=(
            (0, _("Plain")),
            (1, _("Gzip")),
            (2, _("Plain and Gzip")),
            (3, _("Bzip")),
            (4, _("Plain and Bzip")),
            (5, _("Gzip and Bzip")),
            (6, _("All (Recommended)")),
        ),
        default=6,
        help_text=_(
            "Please change the compression method if error occurred when try to rebuild the list."
        )
    )
    packages_validation = models.IntegerField(
        verbose_name=_("Packages Validation"),
        choices=(
            (0, _("No validation")),
            (1, _("MD5Sum")),
            (2, _("MD5Sum & SHA1")),
            (3, _("MD5Sum & SHA1 & SHA256 (Recommended)")),
            (4, _("MD5Sum & SHA1 & SHA256 & SHA512")),
        ),
        default=3,
        help_text=_(
            "You need to update hashes manually."
        ),
    )
    downgrade_support = models.BooleanField(
        verbose_name=_("Downgrade Support"),
        help_text=_(
            "Allow multiple versions to exist in the latest package list."
        ),
        default=True
    )
    advanced_mode = models.BooleanField(
        verbose_name=_("Auto Depiction"),
        help_text=_(
            "Check it to generate awesome depiction page for each version."
        ),
        default=False
    )
    atomic_storage = models.BooleanField(
        verbose_name=_("Atomic Storage"),
        help_text=_(
            "Generate a new copy of package after editing control columns."
        ),
        default=False
    )
    resources_alias = models.CharField(
        # You should not change this field unless you are not using debug server.
        verbose_name=_("Resources Alias"),
        help_text=_("You can specify alias for resources path in Nginx or "
                    "other HTTP servers, which is also necessary for CDN speedup."),
        max_length=255,
        default="/resources/",
        validators=[
            validator_basic,
            validate_alias
        ]
    )
    enable_pdiffs = models.BooleanField(
        verbose_name=_("Enable pdiffs"),
        help_text=_("If package list is extremely large, you should enable this to allow incremental update."),
        default=False,
        validators=[
            validate_pdiffs
        ]
    )
    rest_api = models.BooleanField(
        verbose_name=_("Enable Rest API"),
        help_text=_("Upload packages using HTTP, manage your repositories, snapshots and comments etc."),
        default=True,
        validators=[
            validate_rest_api
        ]
    )
    gpg_signature = models.BooleanField(
        verbose_name=_("Enable GPG Signature"),
        help_text=_("Verify the integrity of the repository. Run 'gpg --gen-key' before you enable this feature."),
        default=False,
        validators=[
            validate_gpg
        ]
    )
    gpg_password = models.CharField(
        verbose_name=_("GPG Password"),
        max_length=255,
        blank=True,
        null=False,
        default=""
    )
    web_server = models.IntegerField(
        verbose_name=_("Web Server"),
        choices=(
            (0, _("Nginx")),
            (1, _("Apache")),
            (2, _("Tomcat")),
        ),
        default=0,
        help_text=_("This will help DCRM redirect download request properly. Only works when \"Redirect Methods\" is "
                    "\"Accel\"."),
        validators=[
            validate_web_server
        ]
    )
    redirect_resources = models.IntegerField(
        verbose_name=_("Redirect Methods"),
        choices=(
            (0, _("None")),
            (1, _("Moved")),
            (2, _("Accel"))
        ),
        help_text=_("None - Read resources and return, without partical support, not recommended.<br />"
                    "Moved - Return 301/302 responses and redirect to the real resource urls.<br />"
                    "Accel - Redirect resource requests to WEB servers without changing urls."),
        default=0,
        validators=[
            
        ]
    )
    redirect_prefix = models.CharField(
        verbose_name=_("Redirect Prefix"),
        max_length=128,
        null=True,
        blank=True,
        help_text=_("Changing scheme and host of the url in package downloading requests, "
                    "which is useful for load balancing or CDN speedup. Only works when \"Redirect Methods\" is "
                    "\"Moved\".<br /> "
                    "Example: https://cdn.82flex.com/"),
        validators=[
            URLValidator,
            validate_slash
        ]
    )
    download_count = models.BooleanField(
        verbose_name=_("Download Count"),
        help_text=_("Count every download. "
                    "You should configure Nginx or other Web servers before you enable this feature."),
        default=False,
        validators=[
            
        ]
        # TODO: Configuration Tutorial for Download Count
    )
    download_cydia_only = models.BooleanField(
        verbose_name=_("Cydia Only"),
        help_text=_("Protect downloading from any other tools except Cydia. "
                       "You should configure Nginx or other Web servers before you enable this feature."),
        default=False,
        validators=[
            
        ]
        # TODO: Configuration Tutorial for Cydia Only
    )
    enable_comments = models.BooleanField(
        verbose_name=_("Comments"),
        help_text=_("Enable comments module"),
        default=False,
    )
    display_social = models.BooleanField(
        verbose_name=_("Social Module"),
        help_text=_("Enable social module"),
        default=False,
    )
    qq_group_name = models.CharField(
        verbose_name=_("QQ Group Name"),
        max_length=128,
        null=True,
        blank=True
    )
    qq_group_url = models.URLField(
        verbose_name=_("QQ Group URL"),
        help_text=_("Display QQ group link on the package info page."),
        max_length=255,
        null=True,
        blank=True,
        validators=[
            URLValidator
        ]
    )
    weibo_name = models.CharField(
        verbose_name=_("Weibo Name"),
        max_length=128,
        null=True,
        blank=True,
    )
    weibo_url = models.URLField(
        verbose_name=_("Weibo URL"),
        help_text=_("Display Weibo link on the package info page."),
        max_length=255,
        null=True,
        blank=True,
        validators=[
            URLValidator
        ]
    )
    alipay_url = models.URLField(
        verbose_name=_("Alipay URL"),
        help_text=_("Display \"Donate via Alipay\" link on the package info page."),
        max_length=255,
        null=True,
        blank=True,
        validators=[
            URLValidator
        ]
    )
    twitter_name = models.CharField(
        verbose_name=_("Twitter Name"),
        max_length=128,
        null=True,
        blank=True
    )
    twitter_url = models.URLField(
        verbose_name=_("Twitter URL"),
        help_text=_("Display Twitter link on the package info page."),
        max_length=255,
        null=True,
        blank=True,
        validators=[
            URLValidator
        ]
    )
    facebook_name = models.CharField(
        verbose_name=_("Facebook Name"),
        max_length=128,
        null=True,
        blank=True
    )
    telegram_name = models.CharField(
        verbose_name=_("Telegram Name"),
        max_length=128,
        null=True,
        blank=True
    )
    telegram_url = models.URLField(
        verbose_name=_("Telegram URL"),
        help_text=_("Display Telegram link on the package info page."),
        max_length=255,
        null=True,
        blank=True,
        validators=[
            URLValidator
        ]
    )
    facebook_url = models.URLField(
        verbose_name=_("Facebook URL"),
        help_text=_("Display Facebook link on the package info page."),
        max_length=255,
        null=True,
        blank=True,
        validators=[
            URLValidator
        ]
    )
    paypal_url = models.URLField(
        verbose_name=_("Paypal URL"),
        help_text=_("Display \"Donate via Paypal\" link on the package info page."),
        max_length=255,
        null=True,
        blank=True,
        validators=[
            URLValidator
        ]
    )
    copyright_year = models.PositiveIntegerField(
        verbose_name=_("Starting Year of Copyright"),
        help_text=_("Leave blank to display current year."),
        null=True,
        blank=True
    )
    copyright_name = models.CharField(
        verbose_name=_("Copyright Name"),
        help_text=_("Corpyright name is displayed on the footer, leave a blank will display the source name."),
        max_length=255,
        null=True,
        blank=True
    )
    footer_icp = models.CharField(
        verbose_name=_("ICP Number"),
        help_text=_("The ICP Number displayed on the footer."),
        max_length=255,
        null=True,
        blank=True
    )
    version_history = models.BooleanField(
        verbose_name=_("Version History"),
        help_text=_("Enable version history module"),
        default=False,
    )
    favicon = models.FileField(
        verbose_name=_("Favicon"),
        max_length=255,
        upload_to="favicon",
        help_text=_("Choose an Icon (*.ico) to upload"),
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['ico'])
        ]
    )
    notice = models.TextField(
        verbose_name=_("Notice"),
        blank=True,
        null=True,
        default="",
        help_text=_("HTML Displayed on the frontend widget and the auto depiction page (mobile).")
    )
    show_notice = models.BooleanField(
        verbose_name=_("Show Notice"),
        default=False,
        help_text=_("Check it to display notice.")
    )
    advertisement = models.TextField(
        verbose_name=_("Advertisement"),
        blank=True,
        null=True,
        default="",
        help_text=_("HTML Displayed on the frontend widget and the auto depiction page (mobile).")
    )
    show_advertisement = models.BooleanField(
        verbose_name=_("Show Advertisement"),
        default=False,
        help_text=_("Check it to display advertisement.")
    )
    external_statistics = models.TextField(
        verbose_name=_("External Statistics"),
        blank=True,
        null=True,
        default="",
        help_text=_("Invisible statistic code.")
    )
    internal_statistics = models.TextField(
        verbose_name=_("Internal Statistics"),
        blank=True,
        null=True,
        default="",
        help_text=_("Statistics code of view information at statistics page.")
    )

    def get_external_favicon_link(self):
        if not self.favicon:
            return None
        file_path = self.favicon.name
        return str(preferences.Setting.resources_alias) + file_path

    favicon_link = property(get_external_favicon_link)

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
