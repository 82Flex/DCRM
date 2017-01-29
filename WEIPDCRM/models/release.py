# coding:utf-8

from __future__ import unicode_literals

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _


class Release(models.Model):
    class Meta:
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
        blank=True
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
        default="",
        help_text=_("In an \"automatic\" repository you might store multiple distributions "
                    "of software for different target systems. For example: apt.saurik.com's "
                    "main repository houses content both for desktop Debian Etch systems as "
                    "well as the iPhone. This codename then describes what distribution we "
                    "are currently looking for. In a \"trivial\" repository (as described in "
                    "this document) you may put anything you want here, and the field may even "
                    "be optional.")
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
        blank=True
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

    icon = models.ImageField(
        verbose_name=_("Repository Icon"),
        upload_to="repository-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True
    )

    def __str__(self):
        return self.label + " (" + self.codename + ")"

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(self.id,)
        )
