# coding:utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.forms import ModelForm
from suit import apps
from suit.widgets import AutosizedTextarea


class ReleaseForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea,
        }


class ReleaseAdmin(admin.ModelAdmin):
    form = ReleaseForm
    actions = [delete_selected]
    list_display = ('origin', 'label', 'codename', 'version', 'created_at')
    search_fields = ['origin', 'label', 'codename']
    readonly_fields = ['created_at']
    fieldsets = [
        ('General', {
            'fields': ['origin', 'label', 'version', 'codename', 'description']
        }),
        ('Appearance', {
            'fields': ['icon']
        }),
        ('Cydia', {
            'fields': ['suite', 'components']
        }),
        ('SEO', {
            'fields': ['keywords']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
    suit_form_size = {
        'widgets': {
            'AutosizedTextarea': apps.SUIT_FORM_SIZE_X_LARGE,
        },
    }
