# coding=utf-8

"""DCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from WEIPDCRM.views.admin import upload
from WEIPDCRM.views.admin.help import about
from WEIPDCRM.views.admin.help import statistics

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/sites/django-rq/', include('django_rq.urls')),
    url(r'^admin/upload/$', upload.upload_view, name='upload'),
    url(r'^admin/upload/version/$', upload.upload_version_view, name='version_add'),
    url(r'^admin/help/about/$', about.about_view, name='help_about'),
    url(r'^admin/help/statistics/$', statistics.statistics_view, name='help_statistics'),
]
