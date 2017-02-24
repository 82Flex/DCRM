# coding=utf-8

# import sys
from django.contrib import admin

# from WEIPDCRM.manage.admin.package import PackageAdmin
from WEIPDCRM.manage.admin.release import ReleaseAdmin
from WEIPDCRM.manage.admin.settings import SettingsAdmin
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

admin.site.disable_action("delete_selected")

# Models (The order should be edited in apps.py)
admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(OSVersion, OSVersionAdmin)
admin.site.register(DeviceType, DeviceTypeAdmin)
admin.site.register(Setting, SettingsAdmin)
admin.site.register(Build, BuildAdmin)
