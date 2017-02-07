# coding:utf-8

from __future__ import unicode_literals

import os
import json
import uuid
import shutil
import hashlib

from django.db import models
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
# from django.db.models.signals import pre_save
# from django.dispatch import receiver
from django.utils.translation import ugettext as _

from preferences import preferences

from WEIPDCRM.models.os_version import OSVersion
from WEIPDCRM.models.device_type import DeviceType
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.debian_package import DebianPackage


class Version(models.Model):
    class Meta:
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")

    # Base Property
    id = models.AutoField(primary_key=True, editable=False)
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=False)
    created_at = models.DateTimeField(verbose_name=_("Created At"), auto_now_add=True)
    download_times = models.IntegerField(verbose_name=_("Download Times"), default=0)

    # File System
    storage = models.FileField(
        verbose_name=_("Storage"),
        upload_to="debs",
    )
    md5 = models.CharField(verbose_name=_("MD5"), max_length=32, default="")
    sha1 = models.CharField(verbose_name=_("SHA1"), max_length=40, default="")
    sha256 = models.CharField(verbose_name=_("SHA256"), max_length=64, default="")
    sha512 = models.CharField(verbose_name=_("SHA512"), max_length=128, default="")
    size = models.BigIntegerField(verbose_name=_("Size"), default=0)

    def update_storage(self):
        # original
        control_field = self.control_field
        path = self.storage.name
        # copy to temporary
        temp_path = 'temp/' + str(uuid.uuid1()) + '.deb'
        shutil.copyfile(path, temp_path)
        # read new package
        temp_package = DebianPackage(temp_path)
        temp_package.control = json.loads(control_field)
        # save new package
        temp_package.save()
        self.storage = temp_package.path
        self.update_hash()
        self.save()

    def update_hash(self):
        path = self.storage.name
        p_size = os.path.getsize(path)
        p_md5 = ''
        p_sha1 = ''
        p_sha256 = ''
        p_sha512 = ''
        hash_type = preferences.Setting.packages_validation
        if hash_type == 0:
            pass
        if hash_type >= 1:
            m2 = hashlib.md5()
            m2.update(path)
            p_md5 = m2.hexdigest()
        if hash_type >= 2:
            m3 = hashlib.sha1()
            m3.update(path)
            p_sha1 = m3.hexdigest()
        if hash_type >= 3:
            m4 = hashlib.sha256()
            m4.update(path)
            p_sha256 = m4.hexdigest()
        if hash_type >= 4:
            m5 = hashlib.sha512()
            m5.update(path)
            p_sha512 = m5.hexdigest()
        self.size = p_size
        self.md5 = p_md5
        self.sha1 = p_sha1
        self.sha256 = p_sha256
        self.sha512 = p_sha512

    # Controls
    package = models.ForeignKey(
        Package,
        verbose_name=_("Package"),
        null=False
    )
    version = models.CharField(
        verbose_name=_("Version"),
        max_length=255,
        help_text=_("A package's version indicates two separate values: the version "
                    "of the software in the package, and the version of the package "
                    "itself. These version numbers are separated by a hyphen."),
        default=_("0.0.1-1")
    )

    # Version Control
    update_logs = models.TextField(
        verbose_name=_("Update Logs"),
        blank=True,
        null=True
    )

    # Compatibility
    os_compatibility = models.ManyToManyField(
        OSVersion,
        verbose_name=_("OS Compatibility"),
        blank=True
    )
    device_compatibility = models.ManyToManyField(
        DeviceType,
        verbose_name=_("Device Compatibility"),
        blank=True
    )

    # Control
    control_field = models.TextField(
        verbose_name=_("Control Field"),
        blank=True,
        null=True
    )

    def __str__(self):
        return self.package.name + ' (' + self.version + ')'

    def get_control_content(self):
        control = json.loads(self.control_field)
        return DebianPackage.get_control_content(control)

    control_content = property(get_control_content)

    def get_external_storage_link(self):
        return '/' + self.storage.name

    storage_link = property(get_external_storage_link)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse(
            "admin:%s_%s_change" % (content_type.app_label, content_type.model),
            args=(self.id,)
        )

# @receiver(pre_save, sender=Version)
# def my_callback(sender, instance, *args, **kwargs):
#     instance.update_hash()
