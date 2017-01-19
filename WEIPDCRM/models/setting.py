from django.db import models
from preferences.models import Preferences
from django.utils.translation import ugettext as _


class Setting(Preferences):
    class Meta:
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")
    packages_compression = models.IntegerField(
        choices=(
            (0, _("plain")),
            (1, _("gzip")),
            (2, _("plain and gzip")),
            (3, _("bzip")),
            (4, _("plain and bzip")),
            (5, _("gzip and bzip")),
            (6, _("all")),
        ),
        default=6,
        help_text=_(
            "Please change the compression method if error occurred when try to rebuild the list."
        )
    )
    packages_validation = models.IntegerField(
        choices=(
            (0, _("No validation")),
            (1, _("MD5Sum")),
            (2, _("MD5Sum & SHA1")),
            (3, _("MD5Sum & SHA1 & SHA256")),
        ),
        default=1,
        help_text=_(
            "It will not take effect until any version edited or added."
        ),
    )
    downgrade_support = models.BooleanField(
        help_text=_(
            "Enable this function will cause a long-term traffic consumption."
        ),
        default=True
    )
    advanced_mode = models.BooleanField(
        help_text=_(
            "Check it to generate awesome depiction page for each version."
        ),
        default=True
    )
