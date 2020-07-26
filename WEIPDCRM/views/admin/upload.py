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

import json
import shutil
import uuid
import os
import re

from django.db import transaction
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.core.files.base import ContentFile

from preferences import preferences

from WEIPDCRM.forms.admin.upload import UploadForm, ImageForm
from WEIPDCRM.models.debian_package import DebianPackage
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.version import Version
from WEIPDCRM.tools import mkdir_p

from photologue.models import Gallery, Photo

if settings.ENABLE_REDIS is True:
    import django_rq
    from django_rq import queues


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
        control = uploaded_package.control
        version_dir = os.path.join(settings.MEDIA_ROOT, 'versions')
        if not os.path.isdir(version_dir):
            mkdir_p(version_dir)
        target_dir = os.path.join(version_dir, str(uuid.uuid1()))
        if not os.path.isdir(target_dir):
            mkdir_p(target_dir)
        target_path = os.path.join(target_dir,
                                   control.get('Package', 'undefined') + '_' +
                                   control.get('Version', 'undefined') + '_' +
                                   control.get('Architecture', 'undefined') + '.deb')
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
                c_package=control.get('Package', None),
                c_version=control.get('Version', None)
            ).last()
            if p_version:
                # version conflict
                result_dict.update({
                    "success": False,
                    "exception": _("Version Conflict: %s") % p_version.c_version
                })
            else:
                # os.rename(path, target_path)
                shutil.move(path, target_path)
                p_version = Version()
                p_version.c_package = control.get('Package', None)
                p_version.c_version = control.get('Version', None)
                p_version.storage = os.path.relpath(target_path, settings.MEDIA_ROOT)
                p_version.maintainer_name = DebianPackage.value_for_field(control.get('Maintainer', None))
                p_version.maintainer_email = DebianPackage.detail_for_field(control.get('Maintainer', None))
                p_version.c_description = control.get('Description', "")
                p_version.c_section = p_section
                p_version.c_tag = control.get('Tag', None)
                p_version.c_architecture = control.get('Architecture', None)
                p_version.c_name = control.get('Name', None)
                p_version.author_name = DebianPackage.value_for_field(control.get('Author', None))
                p_version.author_email = DebianPackage.detail_for_field(control.get('Author', None))
                p_version.sponsor_name = DebianPackage.value_for_field(control.get('Sponsor', None))
                p_version.sponsor_site = DebianPackage.detail_for_field(control.get('Sponsor', None))
                p_version.c_depiction = control.get('Depiction', None)
                p_version.c_homepage = control.get('Homepage', None)
                p_version.c_priority = control.get('Priority', None)
                p_version.c_installed_size = control.get('Installed-Size', None)
                p_version.c_essential = control.get('Essential', None)
                p_version.c_depends = control.get('Depends', None)
                p_version.c_pre_depends = control.get('Pre-Depends', None)
                p_version.c_recommends = control.get('Recommends', None)
                p_version.c_suggests = control.get('Suggests', None)
                p_version.c_breaks = control.get('Breaks', None)
                p_version.c_conflicts = control.get('Conflicts', None)
                p_version.c_replaces = control.get('Replaces', None)
                p_version.c_provides = control.get('Provides', None)
                p_version.c_build_essential = control.get('Build-Essential', None)
                p_version.c_origin = control.get('Origin', None)
                p_version.c_bugs = control.get('Bugs', None)
                p_version.c_multi_arch = control.get('Multi-Arch', None)
                p_version.c_source = control.get('Source', None)
                p_version.c_subarchitecture = control.get('Subarchitecture', None)
                p_version.c_kernel_version = control.get('Kernel-Version', None)
                p_version.c_installer_menu_item = control.get('Installer-Menu-Item', None)
                p_version.c_built_using = control.get('Built-Using', None)
                p_version.c_built_for_profiles = control.get('Built-For-Profiles', None)
                p_version.c_icon = control.get('Icon', None)
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
            # TODO: fix unicode bug
            "exception": str(e)
        })
    return result_dict


def handle_uploaded_screenshot(content):
    """
    :param content: Image info
    :type content: dict
    :return: Result Dict
    :rtype: dict
    """
    result_dict = {}
    try:
        image_dir = os.path.join(settings.MEDIA_ROOT, 'photologue', 'photos')
        if not os.path.isdir(image_dir):
            mkdir_p(image_dir)
        file_name = os.path.basename(content['path'])
        with transaction.atomic():
            content_id = content['id']
            content_slug = content['slug']
            gallery = Gallery.objects.filter(slug=content_slug).last()
            current_site = Site.objects.get(id=settings.SITE_ID)
            p_version = Version.objects.get(id=content_id)
            c_name = re.sub('[^A-Za-z0-9]', '', p_version.c_name)  # filter
            if gallery:
                pass
            else:
                # create a new gallery
                gallery = Gallery.objects.create(title=c_name,
                                                 slug=content_slug,
                                                 description=p_version.c_depiction if p_version.c_depiction else 'None',
                                                 is_public=1)
                gallery.sites.add(current_site)
            # save
            photo = Photo(title=c_name + '_' + str(uuid.uuid1()),
                          slug=c_name.lower() + '_' + str(uuid.uuid1()),
                          caption='',
                          is_public=1)
            data = open(content['path'], 'rb')
            content_file = ContentFile(data.read())
            photo.image.save(file_name, content_file)
            photo.save()
            photo.sites.add(current_site)
            gallery.photos.add(photo)
            data.close()
            if p_version.gallery is None:
                p_version.gallery = gallery
                p_version.save()
            result_dict.update({
                "success": True,
                "version": p_version.id
            })
    except Exception as e:
        # error handler
        result_dict.update({
            "success": False,
            "exception": str(e)
        })
    return result_dict


def handle_uploaded_file(request):
    """
    :param request: Django Request
    :type request: HttpRequest
    """
    f = request.FILES['package']
    temp_root = settings.TEMP_ROOT
    if not os.path.exists(temp_root):
        try:
            mkdir_p(temp_root)
        except OSError:
            pass
    package_temp_path = os.path.join(temp_root, str(uuid.uuid1()) + '.deb')
    with open(package_temp_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    os.chmod(package_temp_path, 0o755)
    if settings.ENABLE_REDIS is True:
        queue = django_rq.get_queue('high')
        return queue.enqueue(handle_uploaded_package, package_temp_path)
    else:
        return handle_uploaded_package(package_temp_path)


def handle_uploaded_image(request, package_id, gallery_slug):
    """
    :param package_id: str
    :param gallery_slug: str
    :param request: Django Request
    :type request: HttpRequest
    """
    i = request.FILES['image']
    temp_root = settings.TEMP_ROOT
    allow_ext = ['.png', '.jpg', '.gif']
    ext = os.path.splitext(i.name)[1].lower()
    if ext in allow_ext:
        if not os.path.exists(temp_root):
            mkdir_p(temp_root)
        image_temp_path = os.path.join(temp_root, str(uuid.uuid1()) + ext)
        with open(image_temp_path, 'wb+') as destination:
            for chunk in i.chunks():
                destination.write(chunk)
        os.chmod(image_temp_path, 0o755)
        content = {
            'id': package_id,
            'slug': gallery_slug,
            'path': image_temp_path
        }
        if settings.ENABLE_REDIS is True:
            queue = django_rq.get_queue('high')
            return queue.enqueue(handle_uploaded_screenshot, content)
        else:
            return handle_uploaded_screenshot(content)
    else:
        result_dict = {
            'success': False,
            'exception': _('Upload failed, unsupported file extension.')
        }
        return result_dict


@staff_member_required
def upload_version_view(request):
    """
    :param request: Django Request
    :return: Redirect Response
    """
    return redirect('upload')


@staff_member_required
def upload_view(request):
    """
    :param request: Django Request
    :return: Http Response
    """
    if preferences.Setting.active_release is None:
        all_msgs = messages.get_messages(request)
        if len(all_msgs) == 0:
            messages.error(request,
                           mark_safe(
                               _("Active release not set: you cannot publish your "
                                 "repository without an active release. <a href=\"%s\">Add Release</a>")
                               % reverse("admin:WEIPDCRM_release_add")
                           ))
    # POST
    if request.method == 'POST':
        # action: upload
        if 'action' in request.POST and request.POST['action'] == 'upload':
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
                        if settings.ENABLE_REDIS is True:
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
                            m_result = handle_uploaded_file(request)
                            succeed = m_result['success']
                            if succeed:
                                result_dict.update({
                                    'status': True,
                                    'msg': _('Upload succeed, proceeding...'),
                                    'job': {
                                        'id': None,
                                        'result': {
                                            'version': m_result['version']
                                        }
                                    }
                                })
                            else:
                                result_dict.update({
                                    'status': False,
                                    'msg': m_result['exception'],
                                    'job': None
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
                    if settings.ENABLE_REDIS is True:
                        m_job = handle_uploaded_file(request)
                        job_id = m_job.id
                        msg = _('Upload succeed, proceeding...')
                    else:
                        m_result = handle_uploaded_file(request)
                        if m_result["success"] is True:
                            return redirect(Version.objects.get(id=int(m_result["version"])).get_admin_url())
                        else:
                            job_id = ''
                            msg = m_result["exception"]
                else:
                    job_id = ''
                    msg = _('Upload failed, invalid form.')
                form = UploadForm()
                context = admin.site.each_context(request)
                context.update({
                    'title': _('Upload New Packages'),
                    'form': form,
                    'job_id': job_id,
                    'msg': msg
                })
                template = 'admin/upload.html'
                return render(request, template, context)
        # action: async-import
        elif 'action' in request.POST and request.POST['action'] == 'async-import':
            if not settings.ENABLE_REDIS:
                messages.error(request, mark_safe(
                    _("To use this action, you must enable <b>Redis Queue</b>.")
                ))
            else:
                items = os.listdir(settings.UPLOAD_ROOT)
                import_items = []
                for item in items:
                    if item[-4:] == ".deb":
                        item_path = os.path.join(settings.UPLOAD_ROOT, item)
                        import_items.append(item_path)
                if len(import_items) > 0:
                    temp_root = settings.TEMP_ROOT
                    if not os.path.exists(temp_root):
                        try:
                            mkdir_p(temp_root)
                        except OSError:
                            pass
                    import_jobs = []
                    queue = django_rq.get_queue('high')
                    for import_item in import_items:
                        package_temp_path = os.path.join(temp_root, str(uuid.uuid1()) + '.deb')
                        shutil.copy(import_item, package_temp_path)
                        os.chmod(package_temp_path, 0o755)
                        import_job = queue.enqueue(handle_uploaded_package, package_temp_path)
                        import_jobs.append(import_job)
                    if len(import_jobs) == 1:
                        messages.info(request, mark_safe(_("{job_count} package importing job have been added to the \"<a href=\"{jobs}\">high</a>\" queue.").format(
                            job_count=str(len(import_jobs)),
                            jobs=reverse('rq_jobs', args=(1, )),
                        )))
                    else:
                        messages.info(request, mark_safe(_("{job_count} package importing jobs have been added to the \"<a href=\"{jobs}\">high</a>\" queue.").format(
                            job_count=str(len(import_jobs)),
                            jobs=reverse('rq_jobs', args=(1, )),
                        )))
                else:
                    messages.warning(request, _("There is no package to import."))
            return redirect('upload')
    # GET
    elif request.method == 'GET':
        form = UploadForm()
        context = admin.site.each_context(request)
        context.update({
            'title': _('Upload New Packages'),
            'form': form,
            'job_id': ''
        })
        template = 'admin/upload.html'
        return render(request, template, context)


@staff_member_required
def upload_screenshots_view(request, package_id, gallery_slug):
    """
    :param package_id: str
    :param gallery_slug: str
    :param request: Django Request
    :return: Http Response
    """
    # POST
    if request.method == "POST":
        # action: upload-img
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
                form = ImageForm(request.POST, request.FILES)
                if form.is_valid():
                    # Handle File
                    if settings.ENABLE_REDIS is True:
                        m_job = handle_uploaded_image(request, package_id, gallery_slug)
                        result_dict.update({
                            'status': True,
                            'msg': _('Upload succeed, proceeding...'),
                            'job': {
                                'id': m_job.id,
                                'result': m_job.result
                            }
                        })
                    else:
                        m_result = handle_uploaded_image(request, package_id, gallery_slug)
                        succeed = m_result['success']
                        if succeed:
                            result_dict.update({
                                'status': True,
                                'msg': _('Upload succeed, proceeding...'),
                                'job': {
                                    'id': None,
                                    'result': {
                                        'version': m_result['version']
                                    }
                                }
                            })
                        else:
                            result_dict.update({
                                'status': False,
                                'msg': m_result['exception'],
                                'job': None
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
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                # Handle File
                if settings.ENABLE_REDIS is True:
                    m_job = handle_uploaded_image(request, package_id, gallery_slug)
                    job_id = m_job.id
                    msg = _('Upload succeed, proceeding...')
                else:
                    m_result = handle_uploaded_image(request, package_id, gallery_slug)
                    if m_result["success"] is True:
                        return redirect(Version.objects.get(id=int(m_result["version"])).get_admin_url())
                    else:
                        job_id = ''
                        msg = m_result["exception"]
            else:
                job_id = ''
                msg = _('Upload failed, invalid form.')
            form = ImageForm()
            context = admin.site.each_context(request)
            context.update({
                'title': _('Upload Screenshots'),
                'form': form,
                'job_id': job_id,
                'msg': msg
            })
            template = 'admin/upload_image.html'
            return render(request, template, context)
    # GET
    elif request.method == 'GET':
        version = Version.objects.get(id=int(package_id))
        name = str(version.c_name) + " " + str(version.c_version)
        form = ImageForm()
        context = admin.site.each_context(request)
        context.update({
            'title': _('Upload Screenshots'),
            'form': form,
            'drop_title': name,
            'job_id': ''
        })
        template = 'admin/upload_image.html'
        return render(request, template, context)
