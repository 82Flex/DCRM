# coding:utf-8

from django.contrib import admin
from manage.admin.package import PackageAdmin
from manage.admin.release import ReleaseAdmin
from manage.admin.settings import SettingsAdmin
from manage.admin.version import VersionAdmin, OSVersionAdmin, DeviceTypeAdmin

from WEIPDCRM.manage.admin.section import SectionAdmin
from WEIPDCRM.models.device_type import DeviceType
from WEIPDCRM.models.os_version import OSVersion
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.release import Release
from WEIPDCRM.models.section import Section
from WEIPDCRM.models.setting import Setting
from WEIPDCRM.models.version import Version

# Settings
admin.site.site_header = "WEIPDCRM"
admin.site.site_title = "WEIPDCRM"

# Models (The order should be edited in apps.py)
admin.site.register(Package, PackageAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(OSVersion, OSVersionAdmin)
admin.site.register(DeviceType, DeviceTypeAdmin)
admin.site.register(Setting, SettingsAdmin)
