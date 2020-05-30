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
import shutil
import subprocess
import uuid

import django_rq
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.actions import delete_selected
from django.contrib.sites.models import Site
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from WEIPDCRM.models.package import Package
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.version import Version
from WEIPDCRM.tools import mkdir_p
from WEIPDCRM.views.admin.upload import handle_uploaded_package

from preferences import preferences


def build_section_package_procedure(conf):
    build_uuid = uuid.uuid4()
    build_path = os.path.join(settings.TEMP_ROOT, str(build_uuid))
    section_path = os.path.join(build_path, 'Applications/Cydia.app/Sections')

    if not os.path.isdir(section_path):
        mkdir_p(section_path)

    # copy section icons
    for section in conf['sections']:
        s_icon = os.path.join(settings.MEDIA_ROOT, section['icon'])
        s_name = section['name'].replace(' ', '_')
        if os.path.isfile(s_icon):
            dest_icon = os.path.join(section_path, s_name + '.png')
            shutil.copyfile(
                s_icon,
                dest_icon
            )
            os.chmod(dest_icon, 0o755)

    # copy gpg signature if needed
    pub_path = '/private/var/mobile/.gpg'
    gpg_enabled = preferences.Setting.gpg_signature
    if gpg_enabled:
        gpg_dest_path = os.path.join(build_path, 'private/var/mobile/.gpg')
        if not os.path.isdir(gpg_dest_path):
            mkdir_p(gpg_dest_path)
        os.chmod(gpg_dest_path, 0o755)
        password = preferences.Setting.gpg_password
        pub_name = "%s.pub" % Site.objects.get(id=settings.SITE_ID).domain
        pub_path = os.path.join(pub_path, pub_name)
        pubkey_path = os.path.join(gpg_dest_path, pub_name)
        if password is not None and len(password) > 0:
            subprocess.check_call(
                ["gpg", "-a", "--export", "--homedir", os.path.join(settings.BASE_DIR, '.gnupg'), "--batch", "--yes", "--pinentry-mode=loopback", "--passphrase", password, "-o",
                 pubkey_path
                 ]
            )
        else:
            subprocess.check_call(
                ["gpg", "-a", "--export", "--homedir", os.path.join(settings.BASE_DIR, '.gnupg'), "--batch", "--yes", "-o",
                 pubkey_path
                 ]
            )

    # generate DEBIAN
    debian_path = os.path.join(build_path, 'DEBIAN')
    if not os.path.isdir(debian_path):
        mkdir_p(debian_path)
    os.chmod(debian_path, 0o755)

    # generate control
    control_detail = conf["control"]
    control_text = \
        """Package: %(package)s
Name: %(name)s
Version: %(version)s
Architecture: %(architecture)s
Section: Repositories
Author: %(author-name)s <%(author-email)s>
Maintainer: %(maintainer-name)s <%(maintainer-email)s>
Sponsor: %(sponsor-name)s <%(sponsor-site)s>
Description: %(description)s
Essential: no
Priority: required
Depends: cydia
""" % control_detail
    control_path = os.path.join(debian_path, 'control')
    with open(control_path, 'wb+') as destination:
        destination.write(control_text.encode("utf-8"))
    os.chmod(control_path, 0o755)

    # generate postinst
    if gpg_enabled:
        postinst_text = \
            """#!/bin/sh
apt-key add "%(pub)s"

""" % ({"pub": pub_path})
        postinst_path = os.path.join(debian_path, 'postinst')
        with open(postinst_path, 'wb+') as destination:
            destination.write(postinst_text.encode("utf-8"))
        os.chmod(postinst_path, 0o755)

    # generate prerm
    if gpg_enabled:
        prerm_text = \
            """#!/bin/sh
apt-key del "%(pub)s"

""" % ({"pub": pub_path})
        prerm_path = os.path.join(debian_path, 'prerm')
        with open(prerm_path, 'wb+') as destination:
            destination.write(prerm_text.encode("utf-8"))
        os.chmod(prerm_path, 0o755)

    # call dpkg to make debian package
    target_dir = os.path.join(settings.TEMP_ROOT, 'packages')
    if not os.path.isdir(target_dir):
        mkdir_p(target_dir)
    pkg_name = "%(package)s_%(version)s_%(architecture)s.deb" % control_detail
    pkg_path = os.path.join(target_dir, pkg_name)
    subprocess.check_call(
        ["dpkg-deb", "-Z", "gzip", "-b", build_path, pkg_path]
    )

    return handle_uploaded_package(pkg_path)


class SectionAdmin(admin.ModelAdmin):
    def generate_icon_package(self, request, queryset):
        """

        :type request: request
        """
        result_set = queryset.values()  # return ValuesQuerySet object
        list_result_set = [entry for entry in result_set]

        site = Site.objects.get(id=settings.SITE_ID)
        scheme = "http"
        if settings.SECURE_SSL is True:
            scheme = "https"
        site_url = "%s://%s" % (scheme, site.domain)

        domain_components = site.domain.split('.')
        domain_components.reverse()
        domain_components.append("source-icon")
        package_identifier = ".".join(domain_components)

        release_label = preferences.Setting.active_release.label
        package_name = _("%s Source Icon") % release_label

        latest_version = Package.objects.filter(c_package=package_identifier).last()
        latest_version_str = None
        if latest_version is not None:
            latest_version = latest_version.get_latest_version()
            if latest_version is not None:
                latest_version_str = latest_version.c_version

        version_str = "0.1"
        latest_num = 0
        if latest_version_str is not None:
            latest_arr = latest_version_str.split('-')
            if len(latest_arr) > 1:
                version_str = latest_arr[0]
                latest_num = int(latest_arr[1])
        new_version_str = '-'.join([version_str, str(latest_num + 1)])

        current_user = request.user
        user_name = current_user.username
        user_email = current_user.email

        conf = {
            "sections": list_result_set,
            "control": {
                "package": package_identifier,
                "name": package_name,
                "version": new_version_str,
                "author-name": user_name,
                "author-email": user_email,
                "maintainer-name": user_name,
                "maintainer-email": user_email,
                "sponsor-name": user_name,
                "sponsor-site": site_url,
                "description": _('Auto generated section icon package for %s.') % release_label,
                "architecture": "iphoneos-arm",
            }
        }
        if settings.ENABLE_REDIS is True:
            queue = django_rq.get_queue('default')
            queue.enqueue(build_section_package_procedure, conf)
            messages.info(request, mark_safe(
                _("Section icon package generating job has been added to the \"<a href=\"%s\">default</a>\" queue.") % (
                    reverse('rq_jobs', args=(0, ))
                )
            ))
        else:
            build_section_package_procedure(conf)
            messages.info(request, _("Section icon package generating job has been finished."))

        return redirect("admin:WEIPDCRM_version_changelist")

    generate_icon_package.short_description = _("Generate icon package for selected sections")

    list_display = ('name', 'created_at')
    search_fields = ['name']
    fieldsets = [
        (_('General'), {
            'fields': ['name']
        }),
        (_('Appearance'), {
            'fields': ['icon']
        }),
        (_('History'), {
            'fields': ['created_at']
        }),
    ]
    actions = [generate_icon_package, delete_selected]

    def has_add_permission(self, request):
        return preferences.Setting.active_release is not None

    def get_readonly_fields(self, request, obj=None):
        """
        You cannot edit section name if any version has assigned to it.
        
        :type obj: Section
        """
        if obj is not None and Version.objects.filter(c_section=obj).count() > 0:
            return ['created_at', 'name']
        else:
            return ['created_at']

    change_form_template = 'admin/section/change_form.html'
