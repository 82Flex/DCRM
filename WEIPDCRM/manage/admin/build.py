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
import bz2
import gzip
import shutil

import hashlib
import subprocess
from PIL import Image

from django.conf import settings
from django.contrib.sites.models import Site
from django.forms import ModelForm

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_rq import queues

from preferences import preferences
from django.contrib.admin.actions import delete_selected
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from suit.widgets import AutosizedTextarea

from WEIPDCRM.models.build import Build
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.version import Version
from WEIPDCRM.models.release import Release
from WEIPDCRM.models.debian_package import DebianPackage

from WEIPDCRM.tools import mkdir_p

if settings.ENABLE_REDIS is True:
    import django_rq


def build_procedure(conf):
    """
    This is the main package list building procedure.
    """
    
    if not conf["build_p_diff"]:
        # Build Package file
        build_all_versions_enabled = conf["build_all"]
        
        # Get Package List QuerySet
        if build_all_versions_enabled:
            version_set = Version.objects.filter(enabled=True).order_by('-id')
            version_count = version_set.count()
        else:
            version_set = Version.objects.raw(
                "SELECT * FROM `WEIPDCRM_version` "
                "WHERE `enabled` = TRUE "
                "GROUP BY `c_package` "
                "ORDER BY `c_package`, `id` DESC"
            )
            version_count = 0
            for version in version_set:
                version_count += 1
        
        # Check Empty
        if version_count == 0:
            raise ValueError(_("No enabled package available."))

        # Preparing Temp Directory
        build_temp_path = os.path.join(settings.TEMP_ROOT, str(conf["build_uuid"]))
        if not os.path.exists(build_temp_path):
            mkdir_p(build_temp_path)

        # Create Temp Package file
        build_temp_package = open(os.path.join(build_temp_path, "Packages"), "wb+")
        
        # Generate Control List
        depiction_url = ""
        if preferences.Setting.advanced_mode:
            site = Site.objects.get(id=settings.SITE_ID)
            scheme = "http"
            if settings.SECURE_SSL is True:
                scheme = "https"
            depiction_url = "%s://%s" % (scheme, site.domain)
        for version_instance in version_set:
            # !!! HERE WE SHOULD USE ADVANCED CONTROL DICT !!!
            control_dict = version_instance.get_advanced_control_dict()
            if (not version_instance.custom_depiction) and len(depiction_url) != 0:
                control_dict["Depiction"] = depiction_url + version_instance.get_absolute_url()
            if version_instance.online_icon is not None and len(str(version_instance.online_icon)) > 0:
                control_dict["Icon"] = depiction_url + os.path.join(str(preferences.Setting.resources_alias), version_instance.online_icon.name)
            DebianPackage.get_control_content(control_dict, build_temp_package)
            build_temp_package.write("\n".encode("utf-8"))
        
        # Compression Gzip
        build_temp_package.seek(0)
        if conf["build_compression"] == 1 \
                or conf["build_compression"] == 2 \
                or conf["build_compression"] == 5 \
                or conf["build_compression"] == 6:
            build_temp_package_gz = gzip.open(os.path.join(build_temp_path, "Packages.gz"), mode="wb")
            while True:
                cache = build_temp_package.read(16 * 1024)  # 16k cache
                if not cache:
                    break
                build_temp_package_gz.write(cache)
            build_temp_package_gz.close()
        
        # Compression Bzip
        build_temp_package.seek(0)
        if conf["build_compression"] == 3 \
                or conf["build_compression"] == 4 \
                or conf["build_compression"] == 5 \
                or conf["build_compression"] == 6:
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
        active_release = Release.objects.get(id=conf["build_release"])
        active_release_control_dict = active_release.get_control_field()
        build_temp_release = open(os.path.join(build_temp_path, "Release"), mode="wb")
        DebianPackage.get_control_content(active_release_control_dict, build_temp_release)
        
        # Checksum
        if conf["build_secure"] is True:
            def hash_file(hash_obj, file_path):
                with open(file_path, "rb") as f:
                    for block in iter(lambda: f.read(65535), b""):
                        hash_obj.update(block)

            checksum_list = [
                "Packages",
                "Packages.gz",
                "Packages.bz2"
            ]
            build_validation_titles = [
                "MD5Sum", "SHA1", "SHA256", "SHA512"
            ]
            build_validation_methods = [
                hashlib.md5, hashlib.sha1, hashlib.sha256, hashlib.sha512
            ]
            
            # Using a loop to iter different validation methods
            for build_validation_index in range(0, 3):
                if conf["build_validation"] > build_validation_index:
                    build_temp_release.write((build_validation_titles[build_validation_index] + ":\n").encode("utf-8"))
                    for checksum_instance in checksum_list:
                        checksum_path = os.path.join(build_temp_path, checksum_instance)
                        if os.path.exists(checksum_path):
                            m2 = build_validation_methods[build_validation_index]()
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

        if conf["build_secure"] is True:
            # GPG Signature
            """
            Use 'gpg --gen-key' to generate GnuPG key before using this function.
            """
            password = preferences.Setting.gpg_password
            if password is not None and len(password) > 0:
                subprocess.check_call(
                    ["gpg", "-abs", "--homedir", os.path.join(settings.BASE_DIR, '.gnupg'), "--batch", "--yes", "--passphrase", password, "-o",
                     os.path.join(build_temp_path, "Release.gpg"),
                     os.path.join(build_temp_path, "Release"),
                     ]
                )
            else:
                subprocess.check_call(
                    ["gpg", "-abs", "--homedir", os.path.join(settings.BASE_DIR, '.gnupg'), "--batch", "--yes", "-o",
                     os.path.join(build_temp_path, "Release.gpg"),
                     os.path.join(build_temp_path, "Release"),
                     ]
                )
        # Preparing Directory
        release_root = os.path.join(
            settings.MEDIA_ROOT,
            "releases",
            str(active_release.id),
        )
        build_path = os.path.join(
            release_root,
            "builds",
            str(conf["build_uuid"])
        )
        if not os.path.isdir(build_path):
            mkdir_p(build_path)
        
        # Publish
        rename_list = [
            "Release",
            "Release.gpg",
            "Packages",
            "Packages.gz",
            "Packages.bz2"
        ]
        for rename_instance in rename_list:
            rename_path = os.path.join(build_temp_path, rename_instance)
            rename_to_path = os.path.join(build_path, rename_instance)
            active_path = os.path.join(release_root, rename_instance)
            if os.path.exists(rename_path):
                if os.path.exists(active_path):
                    os.unlink(active_path)
                shutil.copyfile(rename_path, active_path)
                os.chmod(active_path, 0o755)
                # os.rename(rename_path, rename_to_path)
                shutil.move(rename_path, rename_to_path)
                os.chmod(rename_to_path, 0o755)
            else:
                if os.path.exists(rename_to_path):
                    os.unlink(rename_to_path)
                if os.path.exists(active_path):
                    os.unlink(active_path)

        def thumb_png(png_path):
            img = Image.open(png_path)
            img.thumbnail((60, 60), Image.ANTIALIAS)
            img.save(png_path)
                
        # Cydia Icon
        cydia_icon_path = os.path.join(release_root, "CydiaIcon.png")
        if os.path.exists(cydia_icon_path):
            os.unlink(cydia_icon_path)
        if active_release.icon is not None and len(str(active_release.icon)) > 0:
            src_path = os.path.join(settings.MEDIA_ROOT, active_release.icon.name)
            if os.path.exists(src_path):
                shutil.copyfile(
                    src_path,
                    cydia_icon_path
                )
        else:
            src_path = os.path.join(settings.STATIC_ROOT, "img/CydiaIcon.png")
            if os.path.exists(src_path):
                shutil.copyfile(
                    src_path,
                    cydia_icon_path
                )
        if os.path.exists(cydia_icon_path):
            thumb_png(cydia_icon_path)
            os.chmod(cydia_icon_path, 0o755)

        build_instance = Build.objects.get(uuid=str(conf["build_uuid"]))
        if build_instance is not None:
            build_instance.is_finished = True
            build_instance.save()
    else:
        # TODO: Pdiffs Feature
        pass


class BuildForm(ModelForm):
    class Meta(object):
        widgets = {
            'details': AutosizedTextarea,
        }


class BuildAdmin(admin.ModelAdmin):
    form = BuildForm
    actions = [delete_selected]
    list_display = ('uuid', 'active_release', 'is_finished', 'created_at')
    search_fields = ['uuid']
    fieldsets = [
        (_('General'), {
            'fields': ['active_release', 'job_link', 'details']
        }),
        (_('History'), {
            'fields': ['created_at']
        }),
    ]
    change_form_template = "admin/build/change_form.html"
    change_list_template = "admin/build/change_list.html"

    def job_link(self, obj):
        if obj.job_id is None:
            if obj.is_finished:
                return mark_safe("<img src=\"/static/admin/img/icon-yes.svg\" alt=\"True\" /> %s" % _('Finished'))
            else:
                return mark_safe("<img src=\"/static/admin/img/icon-unknown.svg\" alt=\"Unknown\" /> %s" % _('Unknown'))
        m_job = queues.get_queue('high').fetch_job(obj.job_id)
        if m_job is None:
            return _('No such job')
        if m_job.is_failed:
            status_str = mark_safe("<img src=\"/static/admin/img/icon-no.svg\" alt=\"False\" /> %s" % _('Failed'))
        elif m_job.is_finished:
            if obj.is_finished:
                status_str = mark_safe("<img src=\"/static/admin/img/icon-yes.svg\" alt=\"True\" /> %s" % _('Finished'))
            else:
                status_str = mark_safe(
                    "<img src=\"/static/admin/img/icon-unknown.svg\" alt=\"Unknown\" /> %s" % _('Unknown'))
        else:
            status_str = mark_safe("<img src=\"/static/img/icon-loading.svg\" width=\"13\" alt=\"Loading\" "
                                   "onload=\"setTimeout(function () { window.location.reload(); }, 2000);\" /> "
                                   "%s" % _("Processing..."))
        return mark_safe('<a href="%s" target="_blank">%s</a>' % (
            reverse('rq_job_detail', kwargs={
                'queue_index': 1,
                'job_id': m_job.id
            }),
            status_str
        ))

    job_link.short_description = _("Job")
    job_link.allow_tags = True
    
    def has_add_permission(self, request):
        return preferences.Setting.active_release is not None and Package.objects.count() != 0
    
    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return ['active_release', 'job_link', 'created_at']
        else:
            return ['active_release', 'job_link', 'created_at', 'details']
    
    def save_model(self, request, obj, form, change):
        """
        Set the active release, call building procedure, and then save.
        
        :type obj: Build
        """
        setting = preferences.Setting
        obj.active_release = setting.active_release
        super(BuildAdmin, self).save_model(request, obj, form, change)
        
        if setting.active_release is not None:
            build_args = {
                "build_uuid": obj.uuid,
                "build_all": setting.downgrade_support,
                "build_p_diff": setting.enable_pdiffs,
                "build_compression": setting.packages_compression,
                "build_secure": setting.gpg_signature,
                "build_validation": setting.packages_validation,
                "build_release": obj.active_release.id,
            }
            if settings.ENABLE_REDIS is True:
                queue = django_rq.get_queue('high')
                build_job = queue.enqueue(build_procedure, build_args)
                obj.job_id = build_job.id
                messages.info(request, mark_safe(
                    _("The Build \"<a href=\"{job_detail}\">{obj}</a>\" generating job has been added to the \"<a href=\"{jobs}\">high</a>\" queue.").format(
                        job_detail=reverse('rq_job_detail', kwargs={
                            'queue_index': 1,
                            'job_id': build_job.id,
                        }),
                        obj=str(obj),
                        jobs=reverse('rq_jobs', args=(1, )),
                    )
                ))
            else:
                build_procedure(build_args)
                messages.info(request, _("The Build \"%s\" generating job has been finished.") % str(obj))
            obj.save()
