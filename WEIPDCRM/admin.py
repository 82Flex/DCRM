# coding=utf-8

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

# import sys
from django.contrib import admin

# from WEIPDCRM.manage.admin.package import PackageAdmin
from WEIPDCRM.manage.admin.release import ReleaseAdmin
from WEIPDCRM.manage.admin.setting import SettingAdmin
from WEIPDCRM.manage.admin.version import VersionAdmin
from WEIPDCRM.manage.admin.device_type import DeviceTypeAdmin
from WEIPDCRM.manage.admin.os_version import OSVersionAdmin
from WEIPDCRM.manage.admin.package import PackageAdmin
from WEIPDCRM.manage.admin.section import SectionAdmin
from WEIPDCRM.manage.admin.build import BuildAdmin

from WEIPDCRM.models.device_type import DeviceType
from WEIPDCRM.models.os_version import OSVersion
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.release import Release
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.setting import Setting
from WEIPDCRM.models.version import Version
from WEIPDCRM.models.build import Build

# reload(sys)
# sys.setdefaultencoding('utf-8')

# Settings
admin.site.site_header = "WEIPDCRM"
admin.site.site_title = "WEIPDCRM"

# admin.site.disable_action("delete_selected")

# Models (The order should be edited in apps.py)
admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(OSVersion, OSVersionAdmin)
admin.site.register(DeviceType, DeviceTypeAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(Build, BuildAdmin)
