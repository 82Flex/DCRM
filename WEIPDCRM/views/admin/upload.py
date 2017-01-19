import json
import uuid
from django_rq import job

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.translation import ugettext as _

from WEIPDCRM.forms.admin.upload import UploadForm
from WEIPDCRM.models.debian import DebianPackage


@job('high')
def handle_uploaded_package(p):
    package = DebianPackage(p)
    print(package.control)


@job('high')
def handle_uploaded_file(f):
    package_temp_path = 'temp/' + str(uuid.uuid1()) + '.deb'
    with open(package_temp_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    handle_uploaded_package(package_temp_path)


@staff_member_required
def upload_view(request):
    if request.method == 'POST':
        # Save Package File To Resource Base
        form = UploadForm(request.POST, request.FILES)
        if request.POST['ajax'] == 'true':
            if form.is_valid():
                # Handle File
                handle_uploaded_file.delay(request.FILES['package'])
                message = _('Upload succeed, proceeding...')
            else:
                message = _('Upload failed, invalid form.')
            return HttpResponse(json.dumps({
                'status': form.is_valid(),
                'msg': message,
            }), content_type='application/json')
        else:
            # Redirect to some notify pages
            pass
    else:
        form = UploadForm()
        context = admin.site.each_context(request)
        context.update({
            'title': _('Upload'),
            'form': form
        })
        template = 'admin/upload.html'
        return render(request, template, context)
