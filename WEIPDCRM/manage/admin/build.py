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
import gzip
import bz2
import hashlib

from django_rq import job
from django.conf import settings

from WEIPDCRM.models.debian_package import DebianPackage
from django.contrib import admin
from preferences import preferences
from django.contrib.admin.actions import delete_selected
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from WEIPDCRM.models.build import Build
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.version import Version
from WEIPDCRM.models.release import Release
from WEIPDCRM.models.setting import Setting


@job('high')
def build_procedure(
        build_uuid, build_all, build_p_diff,
        build_compression, build_secure, build_validation,
        build_release):
    """
    This is the main package list building procedure.
    """
    
    if not build_p_diff:
        # Preparing Temp Directory
        build_temp_path = os.path.join(settings.TEMP_ROOT, str(build_uuid))
        if not os.path.exists(build_temp_path):
            os.mkdir(build_temp_path)
        
        # Create Temp Package file
        build_temp_package = open(os.path.join(build_temp_path, "Packages"), "wb+")
        
        # Build Package file
        build_all_versions_enabled = build_all
        
        # Get Package List QuerySet
        if build_all_versions_enabled:
            version_set = Version.objects.filter(enabled=True).order_by('-id')
        else:
            version_set = Package.objects.order_by('-id')
        
        # Generate Control List
        for version_instance in version_set:
            # !!! HERE WE SHOULD USE ADVANCED CONTROL DICT !!!
            control_dict = version_instance.get_advanced_control_dict()
            DebianPackage.get_control_content(control_dict, build_temp_package)
            build_temp_package.write("\n".encode("utf-8"))
        
        # Compression Gzip
        build_temp_package.seek(0)
        if build_compression == 1 or build_compression == 2 or build_compression == 5 or build_compression == 6:
            build_temp_package_gz = gzip.open(os.path.join(build_temp_path, "Packages.gz"), mode="wb")
            while True:
                cache = build_temp_package.read(16 * 1024)  # 16k cache
                if not cache:
                    break
                build_temp_package_gz.write(cache)
            build_temp_package_gz.close()
        
        # Compression Bzip
        build_temp_package.seek(0)
        if build_compression == 3 or build_compression == 4 or build_compression == 5 or build_compression == 6:
            build_temp_package_bz2 = bz2.BZ2File(os.path.join(build_temp_path, "Packages.bz2"), mode="wb")
            while True:
                cache = build_temp_package.read(16 * 1024)  # 16k cache
                if not cache:
                    break
                build_temp_package_bz2.write(cache)
            build_temp_package_bz2.close()
        
        # Close original Package file
        build_temp_package.close()

        # Release
        build_temp_release_path = os.path.join(build_temp_path, "Release")
        active_release = Release.objects.get(id=build_release)
        active_release_control_dict = active_release.get_control_field()
        build_temp_release = open(build_temp_release_path, mode="wb")
        DebianPackage.get_control_content(active_release_control_dict, build_temp_release)
        
        # Checksum
        if build_secure:
            def hash_file(hash_obj, file_path):
                with open(file_path, "rb") as f:
                    for block in iter(lambda: f.read(65535), b""):
                        hash_obj.update(block)

            checksum_list = [
                "Packages",
                "Packages.gz",
                "Packages.bz2"
            ]

            # Perform Checksum Operation
            if build_validation >= 1:
                build_temp_release.write("MD5Sum:\n".encode("utf-8"))
                for checksum_instance in checksum_list:
                    checksum_path = os.path.join(build_temp_path, checksum_instance)
                    if os.path.exists(checksum_path):
                        m2 = hashlib.md5()
                        hash_file(m2, checksum_path)
                        p_hash = m2.hexdigest()
                        p_size = os.path.getsize(checksum_path)
                        build_temp_release.write(
                            (" " + p_hash +
                             " " + str(p_size) +
                             " " + checksum_instance +
                             "\n").encode("utf-8")
                        )
            if build_validation >= 2:
                build_temp_release.write("SHA1:\n".encode("utf-8"))
                for checksum_instance in checksum_list:
                    checksum_path = os.path.join(build_temp_path, checksum_instance)
                    if os.path.exists(checksum_path):
                        m2 = hashlib.sha1()
                        hash_file(m2, checksum_path)
                        p_hash = m2.hexdigest()
                        p_size = os.path.getsize(checksum_path)
                        build_temp_release.write(
                            (" " + p_hash +
                             " " + str(p_size) +
                             " " + checksum_instance +
                             "\n").encode("utf-8")
                        )
            if build_validation >= 3:
                build_temp_release.write("SHA256:\n".encode("utf-8"))
                for checksum_instance in checksum_list:
                    checksum_path = os.path.join(build_temp_path, checksum_instance)
                    if os.path.exists(checksum_path):
                        m2 = hashlib.sha256()
                        hash_file(m2, checksum_path)
                        p_hash = m2.hexdigest()
                        p_size = os.path.getsize(checksum_path)
                        build_temp_release.write(
                            (" " + p_hash +
                             " " + str(p_size) +
                             " " + checksum_instance +
                             "\n").encode("utf-8")
                        )
            if build_validation >= 4:
                build_temp_release.write("SHA512:\n".encode("utf-8"))
                for checksum_instance in checksum_list:
                    checksum_path = os.path.join(build_temp_path, checksum_instance)
                    if os.path.exists(checksum_path):
                        m2 = hashlib.sha512()
                        hash_file(m2, checksum_path)
                        p_hash = m2.hexdigest()
                        p_size = os.path.getsize(checksum_path)
                        build_temp_release.write(
                            (" " + p_hash +
                             " " + str(p_size) +
                             " " + checksum_instance +
                             "\n").encode("utf-8")
                        )
        
        build_temp_release.close()
        
        # TODO: GPG Signature
        
        # Preparing Directory
        build_root_path = os.path.join(settings.MEDIA_ROOT, "builds")
        build_path = os.path.join(build_root_path, str(build_uuid))
        if not os.path.exists(build_path):
            os.mkdir(build_path)
        
        # Move Directory
        rename_list = [
            "Release",
            "Release.gpg",
            "Packages",
            "Packages.gz",
            "Packages.bz2"
        ]
        for rename_instance in rename_list:
            rename_path = os.path.join(build_temp_path, rename_instance)
            if os.path.exists(rename_path):
                rename_to_path = os.path.join(build_path, rename_instance)
                os.rename(rename_path, rename_to_path)
        
        # TODO: Pubish
        
        # TODO: Callback
        
    else:
        # TODO: Pdiffs Feature
        pass


class BuildAdmin(admin.ModelAdmin):
    actions = [delete_selected]
    list_display = ('uuid', 'created_at')
    search_fields = ['uuid']
    readonly_fields = ['uuid', 'created_at']
    fieldsets = [
        ('General', {
            'fields': ['uuid', 'details']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
    change_form_template = "admin/build/change_form.html"
    change_list_template = "admin/build/change_list.html"
    
    def save_model(self, request, obj, form, change):
        """
        Set the active release, call building procedure, and then save.
        
        :type obj: Build
        """
        setting = preferences.Setting
        
        obj.active_release = preferences.Setting.active_release
        super(BuildAdmin, self).save_model(request, obj, form, change)
        build_procedure.delay(
            obj.uuid,  # build_uuid
            setting.downgrade_support,  # build_all
            setting.enable_pdiffs,  # build_p_diff
            setting.packages_compression,  # build_compression
            setting.gpg_signature,  # build_secure
            setting.packages_validation,  # build_validation
            obj.active_release.id,  # build_release
        )
        messages.info(request, _("Build %s generating job has been added to the \"high\" queue.") % str(obj))
