# coding:utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType

from WEIPDCRM.models.section import Section
from WEIPDCRM.models.release import Release


class Package(models.Model):
    class Meta:
        verbose_name = _("Package")
        verbose_name_plural = _("Packages")

    # Base Property
    id = models.AutoField(
        primary_key=True,
        editable=False
    )
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=False)
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        help_text=_("When the package is shown in Cydia's lists, it is convenient "
                    "to have a prettier name. This field allows you to override this "
                    "display with an arbitrary string. This field may change often, "
                    "whereas the \"Package\" field is fixed for the lifetime of the "
                    "package.")
    )
    icon = models.ImageField(
        verbose_name=_("Icon"),
        upload_to="package-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        blank=True,
        null=True
    )

    # Release
    releases = models.ManyToManyField(
        Release,
        verbose_name=_("Releases"),
        blank=True,
    )

    # Controls
    package = models.CharField(
        verbose_name=_("Package"),
        max_length=255,
        help_text=_("This is the \"identifier\" of the package. This should be, entirely "
                    "in lower case, a reversed hostname (much like a \"bundleIdentifier\" "
                    "in Apple's Info.plist files). If you are also choosing to host an "
                    "AppTapp Installer repository to support legacy clients, you are "
                    "strongly encouraged to make this name match the AppTapp bundle "
                    "identifier (except all in lower case)."),
        unique=True
    )
    architecture = models.CharField(
        verbose_name=_("Architecture"),
        max_length=255,
        help_text=_("This describes what system a package is designed for, as .deb files "
                    "are used on everything from the iPhone to your desktop computer. "
                    "The correct value for iPhoneOS 1.0.x/1.1.x is \"darwin-arm\". If "
                    "you are deploying to iPhoneOS 1.2/2.x you should use \"iphoneos-arm\"."),
        default=""
    )
    section = models.ForeignKey(
        Section,
        verbose_name=_("Section"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Under the \"Install\" tab in Cydia, packages are listed by \"Section\". "
                    "If you would like to encode a space into your section name, use an "
                    "underscore (Cydia will automatically convert these).")
    )
    author_name = models.CharField(
        verbose_name=_("Author"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("In contrast, the person who wrote the original software "
                    "is called the \"author\". This name will be shown underneath "
                    "the name of the package on the details screen. The field is "
                    "in the same format as \"Maintainer\".")
    )
    author_email = models.EmailField(
        verbose_name=_("Author Email"),
        max_length=255,
        blank=True,
        null=True
    )
    maintainer_name = models.CharField(
        verbose_name=_("Maintainer"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("It is typically the person who created the package, as opposed to "
                    "the author of the software that was packaged."),
    )
    maintainer_email = models.EmailField(
        verbose_name=_("Maintainer Email"),
        max_length=255,
        blank=True,
        null=True
    )
    sponsor_name = models.CharField(
        verbose_name=_("Sponsor"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Finally, there might be someone who is simply providing the influence "
                    "or the cash to make the package happen. This person should be listed "
                    "here in the form of \"Maintainer\" except using a resource URI instead "
                    "of an e-mail address.")
    )
    sponsor_site = models.URLField(
        verbose_name=_("Sponsor Site"),
        max_length=255,
        blank=True,
        null=True
    )
    depiction = models.URLField(
        verbose_name=_("Depiction"),
        blank=True,
        null=True,
        help_text=_("Pretty much the entire interface of Cydia is a webpage, which makes adding "
                    "features or new functionality remotely very easy. One thing you might want "
                    "is to be able to display custom links or screenshots with special formatting... "
                    "just plain something special (even an advertisement) on your package page. "
                    "This is done with a \"depiction\", which is a URL that is loaded into an iframe, "
                    "replacing the Description: and Homepage: links that are normally presnt. For "
                    "a good example see WinterBoard's package details page in Cydia. For many packagers "
                    "this has simply become their More Information page, which is only used for backwards "
                    "compatibility. It does not need to be the same, however. You also may consider not "
                    "having a Homepage: field at all if you include Depiction:."),
        default=""
    )
    homepage = models.URLField(
        verbose_name=_("Homepage"),
        blank=True,
        null=True,
        default="",
        help_text=_("Often, there is more information that a packager wants to provide about "
                    "a package than can be listed in the description of the package. Cydia "
                    "supports a \"More Info\" field on the details screen that shunts users "
                    "off to a website of the packager's choice.")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True,
        help_text=_("This field is a little more complicated than the others, as it may use "
                    "multiple lines. The first line (after the colon) should contain a short "
                    "description to be displayed on the package lists underneath the name of "
                    "the package. Optionally, one can choose to replace that description with "
                    "an arbitrarily long one that will be displayed on the package details "
                    "screen. Technically the format for this field is quite complicated, but "
                    "most of that complexity is currently ignored by Cydia: instead Cydia allows "
                    "you to place arbitrarily awesome HTML in this field. Each line of this "
                    "extended description must begin with a space. I highly disrecommend using "
                    "this for HTML, however: you should instead use Depiction: for the description "
                    "in Cydia and use extended descriptions (which will then be ignored by Cydia) "
                    "for compatibility with command-line clients. I would normally leave this mess "
                    "undocumented, but this is so different from APT/dpkg that I feel the need to "
                    "do a full explanation here. Arguably, at some future point, I should redo this "
                    "field in Cydia to be parsed correctly, so another way of looking at this is "
                    "that extended descriptions shouldn't be used with Cydia at all."),
        default=""
    )

    def __str__(self):
        return self.package + " (" + self.name + ")"

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(self.id,)
        )
