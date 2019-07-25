# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WEIPDCRM', '0032_setting_gpg_password'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP VIEW `package_view`;"
        ),
        migrations.RunSQL(
            "CREATE VIEW `package_view` AS SELECT `id`, `c_name`, `created_at`, `c_package`, `c_version`, `c_section_id`, `enabled`, `online_icon`, `c_description`, `download_times` AS `download_count` FROM `WEIPDCRM_version` WHERE `id` IN (SELECT MAX(`id`) FROM `WEIPDCRM_version` WHERE `enabled` = TRUE GROUP BY `c_package`) GROUP BY `c_package` ORDER BY `c_package` DESC;"
        ),
    ]
