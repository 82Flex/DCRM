# coding=utf-8
"""
DCRM Upload handling Module
"""

from __future__ import unicode_literals

import json
import uuid
import os

from django_rq import job, queues
from django.db import transaction
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from WEIPDCRM.forms.admin.upload import UploadForm
from WEIPDCRM.models.debian_package import DebianPackage
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.version import Version


@job('high')
def handle_uploaded_package(path):
    """
    :param path: Package Uploaded Path
    :type path: str
    :return: Result Dict
    :rtype: dict
    """
    result_dict = {}
    try:
        uploaded_package = DebianPackage(path)
        # uploaded_package.load()
        control = uploaded_package.control
        target_dir = 'resources/versions/' + str(uuid.uuid1()) + '/'
        os.mkdir(target_dir)
        target_path = target_dir + control.get('Package', 'undefined') + '_' + \
                      control.get('Version', 'undefined') + '_' + \
                      control.get('Architecture', 'undefined') + '.deb'
        with transaction.atomic():
            p_section = Section.objects.filter(name=control.get('Section', None)).last()
            if p_section:
                pass
            else:
                # create a new section
                p_section_name = control.get('Section', None)
                if p_section_name:
                    p_section = Section(name=p_section_name)
                    p_section.save()
            # search version
            p_version = Version.objects.filter(
                package=control.get('Package', None),
                version=control.get('Version', None)
            ).last()
            if p_version:
                # version conflict
                result_dict.update({
                    "success": False,
                    "exception": _("Version Conflict: %s") % p_version.version
                })
            else:
                os.rename(path, target_path)
                p_version = Version()
                p_version.package = control.get('Package', None)
                p_version.version = control.get('Version', None)
                p_version.storage = target_path
                p_version.maintainer_name = DebianPackage.value_for_field(control.get('Maintainer', None))
                p_version.maintainer_email = DebianPackage.detail_for_field(control.get('Maintainer', None))
                p_version.description = control.get('Description', "")
                p_version.section = p_section
                p_version.tag = control.get('Tag', None)
                p_version.architecture = control.get('Architecture', None)
                p_version.name = control.get('Name', None)
                p_version.author_name = DebianPackage.value_for_field(control.get('Author', None))
                p_version.author_email = DebianPackage.detail_for_field(control.get('Author', None))
                p_version.sponsor_name = DebianPackage.value_for_field(control.get('Sponsor', None))
                p_version.sponsor_site = DebianPackage.detail_for_field(control.get('Sponsor', None))
                p_version.depiction = control.get('Depiction', None)
                p_version.homepage = control.get('Homepage', None)
                p_version.priority = control.get('Priority', None)
                p_version.installed_size = control.get('Installed-Size', None)
                p_version.essential = control.get('Essential', None)
                p_version.depends = control.get('Depends', None)
                p_version.pre_depends = control.get('Pre-Depends', None)
                p_version.recommends = control.get('Recommends', None)
                p_version.suggests = control.get('Suggests', None)
                p_version.breaks = control.get('Breaks', None)
                p_version.conflicts = control.get('Conflicts', None)
                p_version.replaces = control.get('Replaces', None)
                p_version.provides = control.get('Provides', None)
                p_version.build_essential = control.get('Build-Essential', None)
                p_version.origin = control.get('Origin', None)
                p_version.bugs = control.get('Bugs', None)
                p_version.multi_arch = control.get('Multi-Arch', None)
                p_version.source = control.get('Source', None)
                p_version.subarchitecture = control.get('Subarchitecture', None)
                p_version.kernel_version = control.get('Kernel-Version', None)
                p_version.installer_menu_item = control.get('Installer-Menu-Item', None)
                p_version.built_using = control.get('Built-Using', None)
                p_version.built_for_profiles = control.get('Built-For-Profiles', None)
                p_version.update_hash()
                p_version.save()
                # move resource
                result_dict.update({
                    "success": True,
                    "version": p_version.id
                })
    except Exception as e:
        # error handler
        result_dict.update({
            "success": False,
            "exception": e.message
        })
    return result_dict


def handle_uploaded_file(request):
    """
    :param request: Django Request
    :type request: HttpRequest
    """
    f = request.FILES['package']
    package_temp_path = 'temp/' + str(uuid.uuid1()) + '.deb'
    with open(package_temp_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return handle_uploaded_package.delay(package_temp_path)


@staff_member_required
def upload_version_view(request):
    """
    :param request: Django Request
    :return: Redirect Response
    """
    messages.info(request, _('Upload a Package File to add new version.'))
    return redirect('upload')


@staff_member_required
def upload_view(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        # Save Package File To Resource Base
        if 'ajax' in request.POST and request.POST['ajax'] == 'true':
            result_dict = {}
            if 'job' in request.POST:
                job_id = request.POST['job']
                result_dict = {}
                m_job = queues.get_queue('high').fetch_job(job_id)
                if m_job is None:
                    result_dict.update({
                        'result': False,
                        'msg': _('No such job'),
                        'job': None
                    })
                else:
                    result_dict.update({
                        'result': True,
                        'msg': '',
                        'job': {
                            'id': m_job.id,
                            'is_failed': m_job.is_failed,
                            'is_finished': m_job.is_finished,
                            'result': m_job.result
                        }
                    })
            else:
                form = UploadForm(request.POST, request.FILES)
                if form.is_valid():
                    # Handle File
                    m_job = handle_uploaded_file(request)
                    result_dict.update({
                        'status': True,
                        'msg': _('Upload succeed, proceeding...'),
                        'job': {
                            'id': m_job.id,
                            'result': m_job.result
                        }
                    })
                else:
                    result_dict.update({
                        'status': False,
                        'msg': _('Upload failed, invalid form.'),
                        'job': None
                    })
            return HttpResponse(json.dumps(result_dict), content_type='application/json')
        else:
            # render upload result
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                # Handle File
                m_job = handle_uploaded_file(request)
                job_id = m_job.id
                msg = _('Upload succeed, proceeding...')
                # messages.success(request, 'Upload succeed, proceeding...')
            else:
                job_id = ''
                msg = _('Upload failed, invalid form.')
                # messages.error(request, 'Upload failed, invalid form.')
            form = UploadForm()
            context = admin.site.each_context(request)
            context.update({
                'title': _('Upload'),
                'form': form,
                'job_id': job_id,
                'msg': msg
            })
            template = 'admin/upload.html'
            return render(request, template, context)
    else:
        form = UploadForm()
        context = admin.site.each_context(request)
        context.update({
            'title': _('Upload'),
            'form': form,
            'job_id': ''
        })
        template = 'admin/upload.html'
        return render(request, template, context)
