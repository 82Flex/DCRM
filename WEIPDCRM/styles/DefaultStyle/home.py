from django.db import transaction
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from WEIPDCRM.models.version import Version

class index(ListView):
    """
    :param request: Django Request
    :return: Django HttpResponse
    :rtype: HttpResponse
    """
    template_name = 'home/index.html'
    context_object_name = 'package_list'
    def get_queryset(self):
        package_list = Version.objects.all()
        return package_list

class package_view(DetailView):
    model = Version
    context_object_name = "package_info"
    pk_url_kwarg = 'package_id'
    template_name = 'home/package.html'

    def get_object(self):
        obj = super(package_view, self).get_object()
        return obj
