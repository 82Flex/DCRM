# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='FluentComment',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('django_comments.comment',),
        ),
    ]
