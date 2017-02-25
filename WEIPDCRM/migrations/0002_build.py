# -*- coding: utf-8 -*-

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

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('WEIPDCRM', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('compression', models.IntegerField(choices=[(0, 'Plain'), (1, 'Gzip'), (2, 'Plain and Gzip'), (3, 'Bzip'), (4, 'Plain and Bzip'), (5, 'Gzip and Bzip'), (6, 'All (Recommended)')], default=6, verbose_name='Packages Compression')),
                ('details', models.TextField(blank=True, null=True, verbose_name='Details')),
                ('active_release', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='WEIPDCRM.Release', verbose_name='Active Release')),
            ],
            options={
                'verbose_name': 'Build',
                'verbose_name_plural': 'Builds',
            },
        ),
    ]
