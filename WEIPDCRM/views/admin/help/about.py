# coding=utf-8
"""
Global Page: About
"""

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.translation import ugettext as _


@staff_member_required
def about_view(request):
    """
    :param request: Django Request
    :return: Django HttpResponse
    :rtype: HttpResponse
    """
    context = admin.site.each_context(request)
    context.update({
        'title': _('About'),
        'version': "4.0 Build 4096",
    })

    template = 'admin/help/about.html'
    return render(request, template, context)
