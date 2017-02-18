# coding=utf-8

from __future__ import unicode_literals

from django import forms


class UploadForm(forms.Form):
    package = forms.FileField()
