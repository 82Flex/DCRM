import json
import uuid
# import hashlib
import os

from django_rq import job, queues
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
# from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from preferences import preferences

from WEIPDCRM.forms.admin.upload import UploadForm
from WEIPDCRM.models.debian_package import DebianPackage
from WEIPDCRM.models.debian_package import BaseVersion
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.version import Version


@job('high')
def handle_uploaded_package(path):
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
        # p_size = os.path.getsize(path)
        # p_md5 = ''
        # p_sha1 = ''
        # p_sha256 = ''
        # p_sha512 = ''
        # hash_type = preferences.Setting.packages_validation
        # if hash_type == 0:
        #     pass
        # if hash_type >= 1:
        #     m2 = hashlib.md5()
        #     m2.update(path)
        #     p_md5 = m2.hexdigest()
        # if hash_type >= 2:
        #     m3 = hashlib.sha1()
        #     m3.update(path)
        #     p_sha1 = m3.hexdigest()
        # if hash_type >= 3:
        #     m4 = hashlib.sha256()
        #     m4.update(path)
        #     p_sha256 = m4.hexdigest()
        # if hash_type >= 4:
        #     m5 = hashlib.sha512()
        #     m5.update(path)
        #     p_sha512 = m5.hexdigest()
        # hash_fields = 'Filename: ' + target_path + '\n'
        # hash_fields += 'Size: ' + str(p_size) + '\n'
        # hash_fields += "MD5sum: " + p_md5 + '\n'
        # hash_fields += "SHA1: " + p_sha1 + '\n'
        # hash_fields += "SHA256: " + p_sha256 + '\n'
        # hash_fields += "SHA512: " + p_sha512 + '\n'
        # search package
        p_package = Package.objects.filter(package=control['Package']).last()
        if p_package:
            p_section = p_package.section
            if p_section:
                pass
        else:
            # search section
            p_section = Section.objects.filter(name=control.get('Section', None)).last()
            if p_section:
                pass
            else:
                # create a new section
                p_section_name = control.get('Section', None)
                if p_section_name:
                    p_section = Section(name=p_section_name)
                    p_section.save()
            # create a new package
            p_package = Package.objects.create(
                name=control.get('Name', _('Untitled Package')),
                package=control.get('Package'),
                section=p_section,
                architecture=control.get('Architecture', None),
                author_name=DebianPackage.value_for_field(control.get('Author', None)),
                author_email=DebianPackage.detail_for_field(control.get('Author', None)),
                sponsor_name=DebianPackage.value_for_field(control.get('Sponsor', None)),
                sponsor_site=DebianPackage.detail_for_field(control.get('Sponsor', None)),
                maintainer_name=DebianPackage.value_for_field(control.get('Maintainer', None)),
                maintainer_email=DebianPackage.detail_for_field(control.get('Maintainer', None)),
                depiction=control.get('Depiction', None),
                homepage=control.get('Homepage', None),
                description=control.get('Description', None)
            )
            # find active release
            p_release = preferences.Setting.active_release
            if p_release:
                p_package.releases.add(p_release)
        # return process
        if p_package:
            result_dict.update({"package": p_package.id})
        if p_section:
            result_dict.update({"section": p_section.id})
        # search version
        p_version = Version.objects.filter(package=p_package, version=control.get('Version', None)).last()
        if p_version:
            # version conflict
            result_dict.update({
                "success": False,
                "exception": _("Version Conflict: %s") % p_version.version
            })
        else:
            p_version = Version(
                package=p_package,
                version=control.get('Version', None),
                control_field=json.dumps(control, sort_keys=True, indent=2),
                storage=target_path,
                # size=p_size,
                # md5=p_md5,
                # sha1=p_sha1,
                # sha256=p_sha256,
                # sha512=p_sha512
            )
            os.rename(path, target_path)
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
    f = request.FILES['package']
    package_temp_path = 'temp/' + str(uuid.uuid1()) + '.deb'
    with open(package_temp_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return handle_uploaded_package.delay(package_temp_path)


@staff_member_required
def upload_version_view(request):
    messages.info(request, _('Upload a Package File to add new version.'))
    return redirect('upload')


@staff_member_required
def upload_view(request):
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
