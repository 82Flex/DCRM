# coding=utf-8

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
import uuid
import shutil
import hashlib

from debian.debian_support import NativeVersion
from debian.deb822 import PkgRelation
from django.dispatch import receiver
from django.urls import reverse
from django.db import models
from django.core import urlresolvers
from django.core.validators import URLValidator
from django.core.validators import validate_slug
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings

from preferences import preferences
from photologue.models import Gallery

from WEIPDCRM.models.os_version import OSVersion
from WEIPDCRM.models.device_type import DeviceType
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.debian_package import DebianPackage

from WEIPDCRM.tools import mkdir_p


if settings.ENABLE_REDIS is True:
    import django_rq


def write_to_package_job(control, path, callback_version_id):
    # copy to temporary
    """
    This job will be called when any field in .deb file control part
    has been edited.
    
    :param control: New Control Dict
    :type control: dict
    :param path: Original Package Path
    :type path: str
    :param callback_version_id: Callback Version ID, for callback query
    :type callback_version_id: int
    """
    abs_path = os.path.join(settings.MEDIA_ROOT, path)
    temp_path = os.path.join(settings.TEMP_ROOT, str(uuid.uuid1()) + '.deb')
    shutil.copyfile(abs_path, temp_path)
    # read new package
    temp_package = DebianPackage(temp_path)
    temp_package.control = control
    # save new package
    temp_package.save()
    t_version = Version.objects.get(id=callback_version_id)
    t_version.write_callback(temp_package.path)


def validate_reversed_domain(value):
    """
    Apple's identifier.
    """
    pattern = re.compile(r"^[0-9A-Za-z.+\-]{2,}$")
    if not pattern.match(value):
        raise ValidationError(
            _("We recommend using a reverse-domain name style string (i.e., com.domainname.appname).")
        )


def validate_version(value):
    """
    Debian standard version format.
    """
    try:
        NativeVersion(value)
    except ValueError as e:
        raise ValidationError(
            _("Invalid version number.")
        )


def validate_name(value):
    """
    Value-Detail based names.
    """
    pattern = re.compile(r"[^<>]")
    if not pattern.match(value):
        raise ValidationError(
            _("Name cannot contain < or >.")
        )


def validate_relations(value):
    """
    Package Lists
    """
    relations = PkgRelation.parse_relations(value)
    for relation in relations:
        for rel in relation:
            if len(rel) == 3:
                raise ValidationError(
                    _("Cannot parse package relationship \"%s\"") % rel.get("name", "untitled")
                )


bugs_validator = URLValidator(
    schemes=["bts-type", "debbugs"],
    message=_("Enter a valid url of the bug tracking system."),
    code="invalid"
)


def validate_bugs(value):
    """
    Inherits from a Built-in URLValidator
    """
    return bugs_validator(value)


class Version(models.Model):
    """
    DCRM Base Model: Version
    This model manages all versions generated from .deb files.
    
    All database fields corresponding to the original control
    part in deb files will be prefixed by 'c_' except foreign keys.
    """
    class Meta(object):
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
    
    @staticmethod
    def get_model_fields(self):
        """
        Access the fields of Version model via _meta table
        :return: An array of fields in Version class
        """
        return self._meta.fields
    
    # Base Property
    id = models.AutoField(
        primary_key=True,
        editable=False
    )
    enabled = models.BooleanField(
        verbose_name=_("Enabled"),
        default=False,
        db_index=True
    )  # OK
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True
    )  # OK
    
    def __str__(self):
        return self.c_package + ' (' + self.c_version + ')'
    
    def get_external_storage_link(self):
        """
        This getter method for storage_link property generates outer
        link for actual downloads.
        
        :return: External Storage Link
         :rtype: str
        """
        ext_path = os.path.join(str(preferences.Setting.resources_alias), self.storage.name)
        return ext_path
    
    storage_link = property(get_external_storage_link)
    
    def get_frontend_storage_link(self):
        """
        This getter method for frontend_link property generates outer
        link for frontend jumps.
        
        :return: External Storage Link
         :rtype: str
        """
        if preferences.Setting.download_count:
            return reverse("package_file_fetch", kwargs={
                'package_id': self.id
            })
        else:
            return self.get_external_storage_link()
    
    frontend_link = property(get_frontend_storage_link)
    
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
    
    @staticmethod
    def get_change_list_url():
        """
        :return: URL String
        :rtype: str
        """
        content_type = ContentType.objects.get_for_model(Version)
        return urlresolvers.reverse(
            "admin:%s_%s_changelist" % (content_type.app_label, content_type.model)
        )
    
    # Compatibility
    os_compatibility = models.ManyToManyField(
        OSVersion,
        verbose_name=_("OS Compatibility"),
        blank=True
    )  # OK
    device_compatibility = models.ManyToManyField(
        DeviceType,
        verbose_name=_("Device Compatibility"),
        blank=True
    )  # OK
    
    # Update Logs
    update_logs = models.TextField(
        verbose_name=_("Update Logs"),
        blank=True,
        default=""
    )  # OK
    
    # File System
    storage = models.FileField(
        verbose_name=_("Storage"),
        upload_to="debs",
        max_length=255
    )  # OK

    # Warning: this field will store icon/file relative to MEDIA_URL,
    #          defined in settings.py.
    online_icon = models.FileField(
        verbose_name=_("Online Icon"),
        upload_to="package-icons",
        help_text=_("Choose an Icon (*.png) to upload"),
        max_length=255,
        blank=True,
        null=True,
    )  # OK

    def get_display_icon(self):
        """
        Get display icon from online_icon field, if not set, then
        return its section icon field
        :return:
        """
        if self.online_icon.name:
            file_path = self.online_icon.name
            return str(preferences.Setting.resources_alias) + file_path
        elif self.c_section:
            # self.c_section.icon has been validated by icon_link getter.
            return self.c_section.icon_link
        return None

    display_icon = property(get_display_icon)
    
    c_icon = models.CharField(
        verbose_name=_("Icon"),
        help_text=_("If there is no \"Online Icon\", this field will be taken."),
        max_length=255,
        null=True,
        blank=True,
        default=None
    )
    c_md5 = models.CharField(
        verbose_name=_("MD5Sum"),
        max_length=32,
        default=""
    )  # OK
    c_sha1 = models.CharField(
        verbose_name=_("SHA1"),
        max_length=40,
        default=""
    )  # OK
    c_sha256 = models.CharField(
        verbose_name=_("SHA256"),
        max_length=64,
        default=""
    )  # OK
    c_sha512 = models.CharField(
        verbose_name=_("SHA512"),
        max_length=128,
        default=""
    )  # OK
    c_size = models.BigIntegerField(
        verbose_name=_("Size"),
        default=0,
        help_text=_("The exact size of the package, in bytes.")
    )  # OK
    download_times = models.IntegerField(
        verbose_name=_("Download Times"),
        default=0,
    )  # OK
    c_installed_size = models.BigIntegerField(
        verbose_name=_("Installed-Size"),
        blank=True,
        null=True,
        default=0,
        help_text=_("The approximate total size of the package's installed files, "
                    "in KiB units.")
    )  # OK
    
    def get_c_installed_size_in_bytes(self):
        return self.c_installed_size * 1024

    c_installed_size_in_bytes = property(get_c_installed_size_in_bytes)
    
    def get_advanced_control_dict(self):
        """
        Generate advanced control dictionary (contains download and verify information).
        
        :rtype: dict
        :return: Advanced Control Dict
        """
        control_dict = self.get_control_dict()
        advanced_dict = {
            "Filename": self.frontend_link,
            "Size": self.c_size,
            "MD5sum": self.c_md5,
            "SHA1": self.c_sha1,
            "SHA256": self.c_sha256,
            "SHA512": self.c_sha512,
        }
        for (k, v) in advanced_dict.items():
            if v is not None and len(str(v)) > 0:
                control_dict[k] = str(v)
        return control_dict
        
    def get_control_dict(self):
        # original
        """
        Generate control dictionary from instance properties
        
        :rtype: dict
        :return: Control Dict
        """
        """
        Standard Keys
        """
        control_field = {
            "Package": self.c_package,
            "Version": self.c_version,
            "Architecture": self.c_architecture,
            "Name": self.c_name,
            "Description": self.c_description,
            "Depiction": self.c_depiction,
            "Homepage": self.c_homepage,
            "Tag": self.c_tag,
            "Priority": self.c_priority,
            "Essential": self.c_essential,
            "Depends": self.c_depends,
            "Pre-Depends": self.c_pre_depends,
            "Recommends": self.c_recommends,
            "Suggests": self.c_suggests,
            "Breaks": self.c_breaks,
            "Conflicts": self.c_conflicts,
            "Replaces": self.c_replaces,
            "Provides": self.c_provides,
            "Origin": self.c_origin,
            "Source": self.c_source,
            "Build-Essential": self.c_build_essential,
            "Bugs": self.c_bugs,
            "Multi-Arch": self.c_multi_arch,
            "Subarchitecture": self.c_subarchitecture,
            "Kernel-Version": self.c_kernel_version,
            "Installer-Menu-Item": self.c_installer_menu_item,
            "Built-Using": self.c_built_using,
            "Built-For-Profiles": self.c_built_for_profiles,
            "Installed-Size": self.c_installed_size,
            "Icon": self.c_icon,
        }
        control = {}
        for (k, v) in control_field.items():
            if v is not None and len(str(v)) > 0:
                control[k] = str(v)
        """
        Foreign Keys
        """
        if self.c_section is not None:
            control.update({"Section": self.c_section.name})
        """
        Value-Detail Keys
        """
        if (self.maintainer_name is not None and len(self.maintainer_name) > 0) and \
                (self.maintainer_email is not None and len(self.maintainer_email) > 0):
            control.update({"Maintainer": self.maintainer_name + " <" + self.maintainer_email + ">"})
        if (self.author_name is not None and len(self.author_name) > 0) and \
                (self.author_email is not None and len(self.author_email) > 0):
            control.update({"Author": self.author_name + " <" + self.author_email + ">"})
        if (self.sponsor_name is not None and len(self.sponsor_name) > 0) and \
                (self.sponsor_site is not None and len(self.sponsor_site) > 0):
            control.update({"Sponsor": self.sponsor_name + " <" + self.sponsor_site + ">"})
        return control
    
    def update_storage(self):
        """
        Update control fields and write to deb files
        This method is executed async.
        """
        control = self.get_control_dict()
        path = self.storage.name
        if settings.ENABLE_REDIS is True:
            queue = django_rq.get_queue('high')
            update_job = queue.enqueue(write_to_package_job, control, path, self.id)
            return update_job
        else:
            write_to_package_job(control, path, self.id)
        return None
    
    def base_filename(self):
        return self.c_package + '_' + self.c_version + '_' + self.c_architecture + '.deb'
        
    def write_callback(self, temp_path):
        """
        The async callback for method update_storage
        :type temp_path: str
        :param temp_path: Created temp deb file for updating result
        :return: No return value
        """
        atomic = preferences.Setting.atomic_storage
        if atomic:
            root_res = os.path.join(settings.MEDIA_ROOT, 'versions')
            if not os.path.isdir(root_res):
                mkdir_p(root_res)
            target_dir = os.path.join(root_res, str(uuid.uuid1()))
            if not os.path.isdir(target_dir):
                mkdir_p(target_dir)
            target_path = os.path.join(target_dir, self.base_filename())
            # os.rename(temp_path, target_path)
            shutil.move(temp_path, target_path)
            os.chmod(target_path, 0o755)
            self.storage.name = os.path.relpath(target_path, settings.MEDIA_ROOT)
        else:
            abs_path = os.path.join(settings.MEDIA_ROOT, self.storage.name)
            os.unlink(abs_path)
            # os.rename(temp_path, abs_path)
            shutil.move(temp_path, abs_path)
            os.chmod(abs_path, 0o755)
        self.update_hash()
        self.save()
    
    def update_hash(self):
        """
        Update hash fields from file system
        :return: No return value
        """

        def hash_file(hash_obj, file_path):
            """
            :param hash_obj: Hash processing instance
            :param file_path: File to be processed
            :type file_path: str
            """
            with open(file_path, str("rb")) as f:
                for block in iter(lambda: f.read(65535), b""):
                    hash_obj.update(block)
        
        path = os.path.join(settings.MEDIA_ROOT, self.storage.name)
        if not os.path.exists(path):
            return
        p_size = os.path.getsize(path)
        p_md5 = ''
        p_sha1 = ''
        p_sha256 = ''
        p_sha512 = ''
        """
        To check hash type for .deb file
        """
        hash_type = preferences.Setting.packages_validation
        if hash_type == 0:
            pass
        if hash_type >= 1:
            m2 = hashlib.md5()
            hash_file(m2, path)
            p_md5 = m2.hexdigest()
        if hash_type >= 2:
            m3 = hashlib.sha1()
            hash_file(m3, path)
            p_sha1 = m3.hexdigest()
        if hash_type >= 3:
            m4 = hashlib.sha256()
            hash_file(m4, path)
            p_sha256 = m4.hexdigest()
        if hash_type >= 4:
            m5 = hashlib.sha512()
            hash_file(m5, path)
            p_sha512 = m5.hexdigest()
        self.c_size = p_size
        self.c_md5 = p_md5
        self.c_sha1 = p_sha1
        self.c_sha256 = p_sha256
        self.c_sha512 = p_sha512
    
    # Required Control
    c_package = models.CharField(
        verbose_name=_("Package"),
        max_length=255,
        help_text=_("This is the \"identifier\" of the package. This should be, entirely "
                    "in lower case, a reversed hostname (much like a \"bundleIdentifier\" "
                    "in Apple's Info.plist files)."),
        validators=[
            validate_reversed_domain
        ],
        db_index=True
    )
    c_version = models.CharField(
        verbose_name=_("Version"),
        max_length=255,
        help_text=_("A package's version indicates two separate values: the version "
                    "of the software in the package, and the version of the package "
                    "itself. These version numbers are separated by a hyphen."),
        default=_("1.0-1"),
        validators=[
            validate_version
        ],
        db_index=True
    )
    
    # Recommend Control
    maintainer_name = models.CharField(
        verbose_name=_("Maintainer"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("It is typically the person who created the package, as opposed to "
                    "the author of the software that was packaged."),
        default="",
        validators=[
            validate_name
        ]
    )
    maintainer_email = models.EmailField(
        verbose_name=_("Maintainer Email"),
        max_length=255,
        blank=True,
        null=True,
        default=""
    )
    c_description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        null=True,
        default="",
        help_text=_("The first line (after the colon) should contain a short description to be "
                    "displayed on the package lists underneath the name of the package. "
                    "Optionally, one can choose to replace that description with "
                    "an arbitrarily long one that will be displayed on the package details "
                    "screen.")
    )
    rich_description = models.TextField(
        verbose_name=_("Rich Description"),
        blank=True,
        null=True,
        default="",
        help_text=_("HTML Displayed on the auto depiction page (mobile).")
    )
    
    # Foreign Keys
    c_section = models.ForeignKey(
        Section,
        verbose_name=_("Section"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Under the \"Install\" tab in Cydia, packages are listed by \"Section\". "
                    "If you would like to encode a space into your section name, use an "
                    "underscore (Cydia will automatically convert these)."),
        default=None
    )
    c_tag = models.TextField(
        verbose_name=_("Tag"),
        blank=True,
        null=True,
        help_text=_("List of tags describing the qualities of the package. The "
                    "description and list of supported tags can be found in the "
                    "debtags package."),
        default=""
    )  # OK
    c_architecture = models.CharField(
        verbose_name=_("Architecture"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("This describes what system a package is designed for, as .deb files "
                    "are used on everything from the iPhone to your desktop computer. "
                    "The correct value for iPhoneOS 1.0.x/1.1.x is \"darwin-arm\". If "
                    "you are deploying to iPhoneOS 1.2/2.x you should use \"iphoneos-arm\"."),
        default="",
        validators=[
            validate_slug
        ]
    )
    
    # Other Controls
    c_name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("When the package is shown in Cydia's lists, it is convenient "
                    "to have a prettier name. This field allows you to override this "
                    "display with an arbitrary string. This field may change often, "
                    "whereas the \"Package\" field is fixed for the lifetime of the "
                    "package."),
        default=_("Untitled Package")
    )
    author_name = models.CharField(
        verbose_name=_("Author"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("In contrast, the person who wrote the original software "
                    "is called the \"author\". This name will be shown underneath "
                    "the name of the package on the details screen. The field is "
                    "in the same format as \"Maintainer\"."),
        default="",
        validators=[
            validate_name
        ]
    )
    author_email = models.EmailField(
        verbose_name=_("Author Email"),
        max_length=255,
        blank=True,
        null=True,
        default=""
    )
    sponsor_name = models.CharField(
        verbose_name=_("Sponsor"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Finally, there might be someone who is simply providing the influence "
                    "or the cash to make the package happen. This person should be listed "
                    "here in the form of \"Maintainer\" except using a resource URI instead "
                    "of an e-mail address."),
        default="",
        validators=[
            validate_name
        ]
    )
    sponsor_site = models.URLField(
        verbose_name=_("Sponsor Site"),
        max_length=255,
        blank=True,
        null=True,
        default=""
    )
    c_depiction = models.URLField(
        verbose_name=_("Depiction"),
        blank=True,
        null=True,
        help_text=_("This is a URL that is loaded into an iframe, replacing the Description: and Homepage: ."),
        default=""
    )
    custom_depiction = models.BooleanField(
        verbose_name=_("Custom Depiction"),
        help_text=_("Exclude this version from Auto Depiction feature."),
        default=False
    )
    c_homepage = models.URLField(
        verbose_name=_("Homepage"),
        blank=True,
        null=True,
        default="",
        help_text=_("Cydia supports a \"More Info\" field on the details screen that shunts users "
                    "off to a website of the packager's choice.")
    )
    
    # Advanced Controls
    c_priority = models.CharField(
        verbose_name=_("Priority"),
        blank=True,
        null=True,
        max_length=255,
        default="",
        choices=(
            (None, "-"),
            ("required", "Required"),
            ("standard", "Standard"),
            ("optional", "Optional"),
            ("extra", "Extra")
        ),
        help_text=_("Sets the importance of this package in relation to the system "
                    "as a whole.  Common priorities are required, standard, "
                    "optional, extra, etc.")
    )
    c_essential = models.CharField(
        verbose_name=_("Essential"),
        blank=True,
        null=True,
        max_length=255,
        default="",
        choices=(
            (None, "-"),
            ("yes", "Yes"),
            ("no", "No")
        ),
        help_text=_("This field is usually only needed when the answer is yes. It "
                    "denotes a package that is required for proper operation of the "
                    "system. Dpkg or any other installation tool will not allow an "
                    "Essential package to be removed (at least not without using "
                    "one of the force options).")
    )
    c_depends = models.TextField(
        verbose_name=_("Depends"),
        blank=True,
        null=True,
        help_text=_("List of packages that are required for this package to provide "
                    "a non-trivial amount of functionality. The package maintenance "
                    "software will not allow a package to be installed if the "
                    "packages listed in its Depends field aren't installed (at "
                    "least not without using the force options).  In an "
                    "installation, the postinst scripts of packages listed in "
                    "Depends fields are run before those of the packages which "
                    "depend on them. On the opposite, in a removal, the prerm "
                    "script of a package is run before those of the packages listed "
                    "in its Depends field."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_pre_depends = models.TextField(
        verbose_name=_("Pre-Depends"),
        blank=True,
        null=True,
        help_text=_("List of packages that must be installed and configured before "
                    "this one can be installed. This is usually used in the case "
                    "where this package requires another package for running its "
                    "preinst script."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_recommends = models.TextField(
        verbose_name=_("Recommends"),
        blank=True,
        null=True,
        help_text=_("Lists packages that would be found together with this one in "
                    "all but unusual installations. The package maintenance "
                    "software will warn the user if they install a package without "
                    "those listed in its Recommends field."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_suggests = models.TextField(
        verbose_name=_("Suggests"),
        blank=True,
        null=True,
        help_text=_("Lists packages that are related to this one and can perhaps "
                    "enhance its usefulness, but without which installing this "
                    "package is perfectly reasonable."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_breaks = models.TextField(
        verbose_name=_("Breaks"),
        blank=True,
        null=True,
        help_text=_("Lists packages that this one breaks, for example by exposing "
                    "bugs when the named packages rely on this one. The package "
                    "maintenance software will not allow broken packages to be "
                    "configured; generally the resolution is to upgrade the "
                    "packages named in a Breaks field."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_conflicts = models.TextField(
        verbose_name=_("Conflicts"),
        blank=True,
        null=True,
        help_text=_("Lists packages that conflict with this one, for example by "
                    "containing files with the same names. The package maintenance "
                    "software will not allow conflicting packages to be installed "
                    "at the same time. Two conflicting packages should each include "
                    "a Conflicts line mentioning the other."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_replaces = models.TextField(
        verbose_name=_("Replaces"),
        blank=True,
        null=True,
        help_text=_("List of packages files from which this one replaces. This is "
                    "used for allowing this package to overwrite the files of "
                    "another package and is usually used with the Conflicts field "
                    "to force removal of the other package, if this one also has "
                    "the same files as the conflicted package."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_provides = models.TextField(
        verbose_name=_("Provides"),
        blank=True,
        null=True,
        help_text=_("This is a list of virtual packages that this one provides. "
                    "Usually this is used in the case of several packages all "
                    "providing the same service. For example, sendmail and exim "
                    "can serve as a mail server, so they provide a common package "
                    "(\"mail-transport-agent\") on which other packages can depend. "
                    "This will allow sendmail or exim to serve as a valid option to "
                    "satisfy the dependency.  This prevents the packages that "
                    "depend on a mail server from having to know the package names "
                    "for all of them, and using \'|\' to separate the list."),
        default="",
        validators=[
            validate_relations
        ]
    )
    
    # Fucking Controls
    c_origin = models.CharField(
        verbose_name=_("Origin"),
        blank=True,
        null=True,
        max_length=255,
        help_text=_("The name of the distribution this package is originating from."),
        default=""
    )  # OK
    c_source = models.CharField(
        verbose_name=_("Source"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("The name of the source package that this binary package came "
                    "from, if it is different than the name of the package itself. "
                    "If the source version differs from the binary version, then "
                    "the source-name will be followed by a source-version in "
                    "parenthesis."),
        default=""
    )  # OK
    c_build_essential = models.CharField(
        verbose_name=_("Build-Essential"),
        blank=True,
        null=True,
        max_length=255,
        default="",
        choices=(
            (None, '-'),
            ("yes", "Yes"),
            ("no", "No")
        ),
        help_text=_("This field is usually only needed when the answer is yes, and "
                    "is commonly injected by the archive software.  It denotes a "
                    "package that is required when building other packages.")
    )
    c_bugs = models.CharField(
        verbose_name=_("Bugs"),
        blank=True,
        null=True,
        max_length=255,
        help_text=_("The url of the bug tracking system for this package. The "
                    "current used format is bts-type://bts-address, like "
                    "debbugs://bugs.debian.org."),
        default="",
        validators=[
            validate_bugs
        ]
    )
    c_multi_arch = models.CharField(
        verbose_name=_("Multi-Arch"),
        blank=True,
        null=True,
        max_length=255,
        choices=(
            ("no", "No"),
            ("same", "Same"),
            ("foreign", "Foreign"),
            ("allowed", "Allowed")
        ),
        help_text=_("This field is used to indicate how this package should behave "
                    "on a multi-arch installations.<br />"
                    "<ul>"
                    "<li>no - This value is the default when the field is omitted, in "
                    "which case adding the field with an explicit no value "
                    "is generally not needed.</li>"
                    "<li>same - This package is co-installable with itself, but it must "
                    "not be used to satisfy the dependency of any package of "
                    "a different architecture from itself.</li>"
                    "<li>foreign - This package is not co-installable with itself, but "
                    "should be allowed to satisfy a non-arch-qualified "
                    "dependency of a package of a different arch from itself "
                    "(if a dependency has an explicit arch-qualifier then "
                    "the value foreign is ignored).</li>"
                    "<li>allowed - This allows reverse-dependencies to indicate in their "
                    "Depends field that they accept this package from a "
                    "foreign architecture by qualifying the package name "
                    "with :any, but has no effect otherwise.</li>"
                    "</ul>"),
        default=""
    )
    c_subarchitecture = models.CharField(
        verbose_name=_("Subarchitecture"),
        max_length=255,
        blank=True,
        null=True,
        default="",
        validators=[
            validate_slug
        ],
    )
    c_kernel_version = models.CharField(
        verbose_name=_("Kernel-Version"),
        max_length=255,
        blank=True,
        null=True,
        default="",
        validators=[
            validate_version
        ]
    )
    c_installer_menu_item = models.TextField(
        verbose_name=_("Installer-Menu-Item"),
        blank=True,
        null=True,
        help_text=_("These fields are used by the debian-installer and are usually "
                    "not needed. See "
                    "/usr/share/doc/debian-installer/devel/modules.txt from the "
                    "debian-installer package for more details about them."),
        default=""
    )  # OK
    c_built_using = models.TextField(
        verbose_name=_("Built-Using"),
        blank=True,
        null=True,
        help_text=_("This field lists extra source packages that were used during "
                    "the build of this binary package.  This is an indication to "
                    "the archive maintenance software that these extra source "
                    "packages must be kept whilst this binary package is "
                    "maintained. This field must be a list of source package names "
                    "with strict \'=\' version relationships.  Note that the archive "
                    "maintenance software is likely to refuse to accept an upload "
                    "which declares a Built-Using relationship which cannot be "
                    "satisfied within the archive."),
        default="",
        validators=[
            validate_relations
        ]
    )
    c_built_for_profiles = models.TextField(
        verbose_name=_("Built-For-Profiles"),
        blank=True,
        null=True,
        help_text=_("This field specifies a whitespace separated list of build "
                    "profiles that this binary packages was built with."),
        default="",
    )  # OK

    # Screenshots
    gallery = models.ForeignKey(
        Gallery,
        verbose_name=_("Gallery"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("You can manage screenshots in Photologue."),
        default=None
    )

    def get_absolute_url(self):
        return reverse('package_id', args=[self.id])


@receiver(models.signals.post_delete, sender=Version)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    :type instance: Version
    """
    if instance.online_icon.name is not None:
        actual_path = os.path.join(settings.MEDIA_ROOT, instance.online_icon.name[1:])
        if os.path.isfile(actual_path):
            os.unlink(actual_path)
    if instance.storage.name is not None:
        actual_path = os.path.join(settings.MEDIA_ROOT, instance.storage.name[1:])
        if os.path.isfile(actual_path):
            os.unlink(actual_path)
