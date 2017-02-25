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

import WEIPDCRM.models.section
import WEIPDCRM.models.setting
import WEIPDCRM.models.version
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('preferences', '0002_auto_20170110_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_name', models.CharField(max_length=255, verbose_name='Name')),
                ('created_at', models.DateTimeField(verbose_name='Created At')),
                ('c_package', models.CharField(max_length=255, verbose_name='Package')),
                ('c_version', models.CharField(max_length=255, verbose_name='Version')),
            ],
            options={
                'verbose_name': 'Package',
                'db_table': 'package_view',
                'managed': False,
                'verbose_name_plural': 'Packages',
            },
        ),
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('enabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('descriptor', models.CharField(help_text='Example: iPhone 7 Plus', max_length=255, verbose_name='Descriptor')),
                ('subtype', models.CharField(help_text='Example: iPhone9,2', max_length=255, verbose_name='Subtype')),
                ('platform', models.CharField(blank=True, help_text='Example: A1661/A1784/A1785', max_length=255, verbose_name='Platform')),
                ('icon', models.ImageField(blank=True, help_text='Choose an Icon (*.png) to upload', upload_to='device-icons', verbose_name='Icon')),
            ],
            options={
                'verbose_name': 'Device Type',
                'verbose_name_plural': 'Device Types',
            },
        ),
        migrations.CreateModel(
            name='OSVersion',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('enabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('descriptor', models.CharField(help_text='Example: 10.2', max_length=255, verbose_name='Version')),
                ('build', models.CharField(help_text='Example: 14C92/11A466', max_length=255, verbose_name='Build')),
                ('icon', models.ImageField(blank=True, help_text='Choose an Icon (*.png) to upload', upload_to='os-icons', verbose_name='Icon')),
            ],
            options={
                'verbose_name': 'iOS Version',
                'verbose_name_plural': 'iOS Versions',
            },
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('origin', models.CharField(default='', help_text='This is used by Cydia as the name of the repository as shown in the source editor (and elsewhere). This should be a longer, but not insanely long, description of the repository.', max_length=255, verbose_name='Origin')),
                ('label', models.CharField(default='', help_text="On the package list screens, Cydia shows what repository and section packages came from. This location doesn't have much room, though, so this field should contain a shorter/simpler version of the name of the repository that can be used as a tag.", max_length=255, verbose_name='Label')),
                ('suite', models.CharField(blank=True, default='stable', help_text='Just set this to "stable". This field might not be required, but who really knows? I, for certain, do not.', max_length=255, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='Suite')),
                ('version', models.CharField(default='0.0.1-1', help_text='This is an arbitrary version number that nothing actually parses. I am going to look into seeing how required it is.', max_length=255, verbose_name='Version')),
                ('codename', models.CharField(blank=True, default='', help_text='In an "automatic" repository you might store multiple distributions of software for different target systems. For example: apt.saurik.com\'s main repository houses content both for desktop Debian Etch systems as well as the iPhone. This codename then describes what distribution we are currently looking for.', max_length=255, verbose_name='Codename')),
                ('architectures', models.CharField(blank=True, default='iphoneos-arm', help_text='To verify a repository is for the specific device you are working with APT looks in the release file for this list. You must specify all of the architectures that appear in your Packages file here. Again, we use darwin-arm for 1.1.x and iphoneos-arm for 2.x.', max_length=255, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='Architectures')),
                ('components', models.CharField(blank=True, default='main', help_text='Just set this to "main". This field might not be required, but who really knows? I, for certain, do not.', max_length=255, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='Components')),
                ('description', models.TextField(blank=True, help_text='On the package source screen a short description is listed of the repository. This description may eventually work similarly to that of a package (with a long/short variety and the aforementioned encoding), but for right now only the shorter description is displayed directly on the list.', verbose_name='Description')),
                ('keywords', models.CharField(blank=True, default='', help_text='Separated by commas.', max_length=255, verbose_name='Keywords')),
                ('icon', models.ImageField(blank=True, help_text='Choose an Icon (*.png) to upload', upload_to='repository-icons', verbose_name='Repository Icon')),
            ],
            options={
                'verbose_name': 'Release',
                'verbose_name_plural': 'Releases',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('name', models.CharField(help_text='This is a general field that gives the package a category based on the software that it installs. You will not be able to edit its name after assigning any package under it.', max_length=255, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid'), WEIPDCRM.models.section.validator_underscore], verbose_name='Name')),
                ('icon', models.ImageField(blank=True, help_text='Choose an Icon (*.png) to upload', null=True, upload_to='section-icons', verbose_name='Icon')),
            ],
            options={
                'verbose_name': 'Section',
                'verbose_name_plural': 'Sections',
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('preferences_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='preferences.Preferences')),
                ('packages_compression', models.IntegerField(choices=[(0, 'Plain'), (1, 'Gzip'), (2, 'Plain and Gzip'), (3, 'Bzip'), (4, 'Plain and Bzip'), (5, 'Gzip and Bzip'), (6, 'All (Recommended)')], default=6, help_text='Please change the compression method if error occurred when try to rebuild the list.', verbose_name='Packages Compression')),
                ('packages_validation', models.IntegerField(choices=[(0, 'No validation'), (1, 'MD5Sum'), (2, 'MD5Sum & SHA1'), (3, 'MD5Sum & SHA1 & SHA256 (Recommended)'), (4, 'MD5Sum & SHA1 & SHA256 & SHA512')], default=3, help_text='You need to update hashes manually.', verbose_name='Packages Validation')),
                ('downgrade_support', models.BooleanField(default=True, help_text='Allow multiple versions to exist in the latest package list.', verbose_name='Downgrade Support')),
                ('advanced_mode', models.BooleanField(default=True, help_text='Check it to generate awesome depiction page for each version.', verbose_name='Auto Depiction')),
                ('atomic_storage', models.BooleanField(default=False, help_text='Generate a new copy of package after editing control columns.', verbose_name='Atomic Storage')),
                ('resources_alias', models.CharField(default='/resources/', help_text='You can specify alias for resources path in Nginx or other HTTP servers, which is necessary for CDN speedup.', max_length=255, validators=[WEIPDCRM.models.setting.validator_basic, WEIPDCRM.models.setting.validate_alias], verbose_name='Resources Alias')),
                ('enable_pdiffs', models.BooleanField(default=False, help_text='If package list is extremely large, you should enable this to allow incremental update.', verbose_name='Enable pdiffs')),
                ('rest_api', models.BooleanField(default=False, help_text='Upload packages using HTTP, manage your repositories, snapshots, published repositories etc.', verbose_name='Enable Rest API')),
                ('active_release', models.ForeignKey(blank=True, help_text='Each repository should have an active release, otherwise it will not be recognized by any advanced package tools.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='WEIPDCRM.Release', verbose_name='Active Release')),
            ],
            options={
                'verbose_name': 'Setting',
                'verbose_name_plural': 'Settings',
            },
            bases=('preferences.preferences',),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('enabled', models.BooleanField(db_index=True, default=False, verbose_name='Enabled')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('update_logs', models.TextField(blank=True, default='', verbose_name='Update Logs')),
                ('storage', models.FileField(max_length=255, upload_to='debs', verbose_name='Storage')),
                ('c_icon', models.ImageField(blank=True, default='', help_text='Choose an Icon (*.png) to upload', upload_to='package-icons', verbose_name='Icon')),
                ('c_md5', models.CharField(default='', max_length=32, verbose_name='MD5Sum')),
                ('c_sha1', models.CharField(default='', max_length=40, verbose_name='SHA1')),
                ('c_sha256', models.CharField(default='', max_length=64, verbose_name='SHA256')),
                ('c_sha512', models.CharField(default='', max_length=128, verbose_name='SHA512')),
                ('c_size', models.BigIntegerField(default=0, help_text='The exact size of the package, in bytes.', verbose_name='Size')),
                ('download_times', models.IntegerField(default=0, verbose_name='Download Times')),
                ('c_installed_size', models.BigIntegerField(blank=True, default=0, help_text="The approximate total size of the package's installed files, in KiB units.", null=True, verbose_name='Installed-Size')),
                ('c_package', models.CharField(db_index=True, help_text='This is the "identifier" of the package. This should be, entirely in lower case, a reversed hostname (much like a "bundleIdentifier" in Apple\'s Info.plist files).', max_length=255, validators=[WEIPDCRM.models.version.validate_reversed_domain], verbose_name='Package')),
                ('c_version', models.CharField(db_index=True, default='1.0-1', help_text="A package's version indicates two separate values: the version of the software in the package, and the version of the package itself. These version numbers are separated by a hyphen.", max_length=255, validators=[WEIPDCRM.models.version.validate_version], verbose_name='Version')),
                ('maintainer_name', models.CharField(blank=True, default='', help_text='It is typically the person who created the package, as opposed to the author of the software that was packaged.', max_length=255, null=True, validators=[WEIPDCRM.models.version.validate_name], verbose_name='Maintainer')),
                ('maintainer_email', models.EmailField(blank=True, default='', max_length=255, null=True, verbose_name='Maintainer Email')),
                ('c_description', models.TextField(blank=True, default='', help_text='The first line (after the colon) should contain a short description to be displayed on the package lists underneath the name of the package. Optionally, one can choose to replace that description with an arbitrarily long one that will be displayed on the package details screen.', null=True, verbose_name='Description')),
                ('c_tag', models.TextField(blank=True, default='', help_text='List of tags describing the qualities of the package. The description and list of supported tags can be found in the debtags package.', null=True, verbose_name='Tag')),
                ('c_architecture', models.CharField(blank=True, default='', help_text='This describes what system a package is designed for, as .deb files are used on everything from the iPhone to your desktop computer. The correct value for iPhoneOS 1.0.x/1.1.x is "darwin-arm". If you are deploying to iPhoneOS 1.2/2.x you should use "iphoneos-arm".', max_length=255, null=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='Architecture')),
                ('c_name', models.CharField(blank=True, default='Untitled Package', help_text='When the package is shown in Cydia\'s lists, it is convenient to have a prettier name. This field allows you to override this display with an arbitrary string. This field may change often, whereas the "Package" field is fixed for the lifetime of the package.', max_length=255, null=True, verbose_name='Name')),
                ('author_name', models.CharField(blank=True, default='', help_text='In contrast, the person who wrote the original software is called the "author". This name will be shown underneath the name of the package on the details screen. The field is in the same format as "Maintainer".', max_length=255, null=True, validators=[WEIPDCRM.models.version.validate_name], verbose_name='Author')),
                ('author_email', models.EmailField(blank=True, default='', max_length=255, null=True, verbose_name='Author Email')),
                ('sponsor_name', models.CharField(blank=True, default='', help_text='Finally, there might be someone who is simply providing the influence or the cash to make the package happen. This person should be listed here in the form of "Maintainer" except using a resource URI instead of an e-mail address.', max_length=255, null=True, validators=[WEIPDCRM.models.version.validate_name], verbose_name='Sponsor')),
                ('sponsor_site', models.URLField(blank=True, default='', max_length=255, null=True, verbose_name='Sponsor Site')),
                ('c_depiction', models.URLField(blank=True, default='', help_text='This is a URL that is loaded into an iframe, replacing the Description: and Homepage: .', null=True, verbose_name='Depiction')),
                ('custom_depiction', models.BooleanField(default=False, help_text='Exclude this version from Auto Depiction feature.', verbose_name='Custom Depiction')),
                ('c_homepage', models.URLField(blank=True, default='', help_text='Cydia supports a "More Info" field on the details screen that shunts users off to a website of the packager\'s choice.', null=True, verbose_name='Homepage')),
                ('c_priority', models.CharField(blank=True, choices=[(None, '-'), ('required', 'Required'), ('standard', 'Standard'), ('optional', 'Optional'), ('extra', 'Extra')], default='', help_text='Sets the importance of this package in relation to the system as a whole.  Common priorities are required, standard, optional, extra, etc.', max_length=255, null=True, verbose_name='Priority')),
                ('c_essential', models.CharField(blank=True, choices=[(None, '-'), ('yes', 'Yes'), ('no', 'No')], default='', help_text='This field is usually only needed when the answer is yes. It denotes a package that is required for proper operation of the system. Dpkg or any other installation tool will not allow an Essential package to be removed (at least not without using one of the force options).', max_length=255, null=True, verbose_name='Essential')),
                ('c_depends', models.TextField(blank=True, default='', help_text="List of packages that are required for this package to provide a non-trivial amount of functionality. The package maintenance software will not allow a package to be installed if the packages listed in its Depends field aren't installed (at least not without using the force options).  In an installation, the postinst scripts of packages listed in Depends fields are run before those of the packages which depend on them. On the opposite, in a removal, the prerm script of a package is run before those of the packages listed in its Depends field.", null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Depends')),
                ('c_pre_depends', models.TextField(blank=True, default='', help_text='List of packages that must be installed and configured before this one can be installed. This is usually used in the case where this package requires another package for running its preinst script.', null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Pre-Depends')),
                ('c_recommends', models.TextField(blank=True, default='', help_text='Lists packages that would be found together with this one in all but unusual installations. The package maintenance software will warn the user if they install a package without those listed in its Recommends field.', null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Recommends')),
                ('c_suggests', models.TextField(blank=True, default='', help_text='Lists packages that are related to this one and can perhaps enhance its usefulness, but without which installing this package is perfectly reasonable.', null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Suggests')),
                ('c_breaks', models.TextField(blank=True, default='', help_text='Lists packages that this one breaks, for example by exposing bugs when the named packages rely on this one. The package maintenance software will not allow broken packages to be configured; generally the resolution is to upgrade the packages named in a Breaks field.', null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Breaks')),
                ('c_conflicts', models.TextField(blank=True, default='', help_text='Lists packages that conflict with this one, for example by containing files with the same names. The package maintenance software will not allow conflicting packages to be installed at the same time. Two conflicting packages should each include a Conflicts line mentioning the other.', null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Conflicts')),
                ('c_replaces', models.TextField(blank=True, default='', help_text='List of packages files from which this one replaces. This is used for allowing this package to overwrite the files of another package and is usually used with the Conflicts field to force removal of the other package, if this one also has the same files as the conflicted package.', null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Replaces')),
                ('c_provides', models.TextField(blank=True, default='', help_text='This is a list of virtual packages that this one provides. Usually this is used in the case of several packages all providing the same service. For example, sendmail and exim can serve as a mail server, so they provide a common package ("mail-transport-agent") on which other packages can depend. This will allow sendmail or exim to serve as a valid option to satisfy the dependency.  This prevents the packages that depend on a mail server from having to know the package names for all of them, and using \'|\' to separate the list.', null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Provides')),
                ('c_origin', models.CharField(blank=True, default='', help_text='The name of the distribution this package is originating from.', max_length=255, null=True, verbose_name='Origin')),
                ('c_source', models.CharField(blank=True, default='', help_text='The name of the source package that this binary package came from, if it is different than the name of the package itself. If the source version differs from the binary version, then the source-name will be followed by a source-version in parenthesis.', max_length=255, null=True, verbose_name='Source')),
                ('c_build_essential', models.CharField(blank=True, choices=[(None, '-'), ('yes', 'Yes'), ('no', 'No')], default='', help_text='This field is usually only needed when the answer is yes, and is commonly injected by the archive software.  It denotes a package that is required when building other packages.', max_length=255, null=True, verbose_name='Build-Essential')),
                ('c_bugs', models.CharField(blank=True, default='', help_text='The url of the bug tracking system for this package. The current used format is bts-type://bts-address, like debbugs://bugs.debian.org.', max_length=255, null=True, validators=[WEIPDCRM.models.version.validate_bugs], verbose_name='Bugs')),
                ('c_multi_arch', models.CharField(blank=True, choices=[('no', 'No'), ('same', 'Same'), ('foreign', 'Foreign'), ('allowed', 'Allowed')], default='', help_text='This field is used to indicate how this package should behave on a multi-arch installations.<br /><ul><li>no - This value is the default when the field is omitted, in which case adding the field with an explicit no value is generally not needed.</li><li>same - This package is co-installable with itself, but it must not be used to satisfy the dependency of any package of a different architecture from itself.</li><li>foreign - This package is not co-installable with itself, but should be allowed to satisfy a non-arch-qualified dependency of a package of a different arch from itself (if a dependency has an explicit arch-qualifier then the value foreign is ignored).</li><li>allowed - This allows reverse-dependencies to indicate in their Depends field that they accept this package from a foreign architecture by qualifying the package name with :any, but has no effect otherwise.</li></ul>', max_length=255, null=True, verbose_name='Multi-Arch')),
                ('c_subarchitecture', models.CharField(blank=True, default='', max_length=255, null=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='Subarchitecture')),
                ('c_kernel_version', models.CharField(blank=True, default='', max_length=255, null=True, validators=[WEIPDCRM.models.version.validate_version], verbose_name='Kernel-Version')),
                ('c_installer_menu_item', models.TextField(blank=True, default='', help_text='These fields are used by the debian-installer and are usually not needed. See /usr/share/doc/debian-installer/devel/modules.txt from the debian-installer package for more details about them.', null=True, verbose_name='Installer-Menu-Item')),
                ('c_built_using', models.TextField(blank=True, default='', help_text="This field lists extra source packages that were used during the build of this binary package.  This is an indication to the archive maintenance software that these extra source packages must be kept whilst this binary package is maintained. This field must be a list of source package names with strict '=' version relationships.  Note that the archive maintenance software is likely to refuse to accept an upload which declares a Built-Using relationship which cannot be satisfied within the archive.", null=True, validators=[WEIPDCRM.models.version.validate_relations], verbose_name='Built-Using')),
                ('c_built_for_profiles', models.TextField(blank=True, default='', help_text='This field specifies a whitespace separated list of build profiles that this binary packages was built with.', null=True, verbose_name='Built-For-Profiles')),
                ('c_section', models.ForeignKey(blank=True, default=None, help_text='Under the "Install" tab in Cydia, packages are listed by "Section". If you would like to encode a space into your section name, use an underscore (Cydia will automatically convert these).', null=True, on_delete=django.db.models.deletion.SET_NULL, to='WEIPDCRM.Section', verbose_name='Section')),
                ('device_compatibility', models.ManyToManyField(blank=True, to='WEIPDCRM.DeviceType', verbose_name='Device Compatibility')),
                ('os_compatibility', models.ManyToManyField(blank=True, to='WEIPDCRM.OSVersion', verbose_name='OS Compatibility')),
            ],
            options={
                'verbose_name': 'Version',
                'verbose_name_plural': 'Versions',
            },
        ),
        migrations.RunSQL(
            "CREATE VIEW `package_view` AS SELECT `WEIPDCRM_version`.* FROM `WEIPDCRM_version` WHERE `WEIPDCRM_version`.`enabled` = TRUE GROUP BY `WEIPDCRM_version`.`c_package` DESC;"
        ),
        migrations.RunSQL(
            "INSERT INTO `WEIPDCRM_devicetype` VALUES ('1', '1', '2017-02-23 20:40:06.081991', 'iPod Touch 4G', 'iPod4,1', 'A1367', ''), ('2', '1', '2017-02-23 20:40:31.481875', 'iPod Touch 5G', 'iPod5,1', 'A1421/A1509', ''), ('3', '1', '2017-02-23 20:41:11.038126', 'iPod Touch 6G', 'iPod7,1', 'A1574', ''), ('4', '1', '2017-02-23 20:42:41.308309', 'iPad 3', 'iPad3,1/iPad3,2/iPad3,3', 'A1416/A1403/A1430', ''), ('5', '1', '2017-02-23 20:43:14.274605', 'iPad 4', 'iPad3,4/iPad3,5/iPad3,6', 'A1458/A1459/A1460', ''), ('6', '1', '2017-02-23 20:43:46.963973', 'iPad Air', 'iPad4,1/iPad4,2/iPad4,3', 'A1474/A1475/A1476', ''), ('7', '1', '2017-02-23 20:44:19.633470', 'iPad Air 2', 'iPad5,3/iPad5,4', 'A1566/A1567', ''), ('8', '1', '2017-02-23 20:45:02.227205', 'iPad Mini 2', 'iPad4,4/iPad4,5/iPad4,6', 'A1489/A1490/A1491', ''), ('9', '1', '2017-02-23 20:45:35.967523', 'iPad Mini 3', 'iPad4,7/iPad4,8/iPad4,9', 'A1599/A1600/A1601', ''), ('10', '1', '2017-02-23 20:46:04.407481', 'iPad Mini 4', 'iPad5,1/iPad5,2', 'A1538/A1550', ''), ('11', '1', '2017-02-23 20:46:28.145065', 'iPad Pro (12.9 inch)', 'iPad6,7/iPad6,8', 'A1584/A1652', ''), ('12', '1', '2017-02-23 20:46:53.761824', 'iPad Pro (9.7 inch)', 'iPad6,3/iPad6,4', 'A1673/A1674/A1675', ''), ('13', '1', '2017-02-23 20:48:19.262702', 'iPhone 4', 'iPhone3,1/iPhone3,2/iPhone3,3', 'A1349/A1332', ''), ('14', '1', '2017-02-23 20:48:43.484709', 'iPhone 4S', 'iPhone4,1', 'A1431/A1387', ''), ('15', '1', '2017-02-23 20:49:18.146555', 'iPhone 5', 'iPhone5,1/iPhone5,2', 'A1428/A1429/A1442', ''), ('16', '1', '2017-02-23 20:50:02.325370', 'iPhone 5C', 'iPhone5,3/iPhone5,4', 'A1532/A1456/A1507/A1529/A1516/A1526', ''), ('17', '1', '2017-02-23 20:50:46.258417', 'iPhone 5S', 'iPhone6,1/iPhone6,2', 'A1533/A1453/A1457/A1530/A1518/A1528', ''), ('18', '1', '2017-02-23 20:51:15.283135', 'iPhone 6', 'iPhone7,2', 'A1549/A1586/A1589', ''), ('19', '1', '2017-02-23 20:51:37.017890', 'iPhone 6 Plus', 'iPhone7,1', 'A1522/A1524/A1593', ''), ('20', '1', '2017-02-23 20:52:07.123383', 'iPhone 6S', 'iPhone8,1', 'A1633/A1688/A1700/A1691', ''), ('21', '1', '2017-02-23 20:52:27.778077', 'iPhone 6S Plus', 'iPhone8,2', 'A1634/A1687/A1699/A1690', ''), ('22', '1', '2017-02-23 20:52:54.655229', 'iPhone SE', 'iPhone8,4', 'A1662/A1723/A1724', ''), ('23', '1', '2017-02-23 20:53:26.954602', 'iPhone 7', 'iPhone9,1/iPhone9,3', 'A1660/A1778/A1779', ''), ('24', '1', '2017-02-23 20:53:54.574175', 'iPhone 7 Plus', 'iPhone9,2/iPhone9,4', 'A1661/A1784/A1785', '');"
        ),
        migrations.RunSQL(
            "INSERT INTO `WEIPDCRM_osversion` VALUES ('1', '1', '2017-02-23 20:26:07.999147', '7.0', '11A465/11A466', ''), ('2', '1', '2017-02-23 20:26:27.234628', '7.0.1', '11A470a', ''), ('3', '1', '2017-02-23 20:26:35.694836', '7.0.2', '11A501', ''), ('4', '1', '2017-02-23 20:26:45.968797', '7.0.3', '11B511', ''), ('5', '1', '2017-02-23 20:26:55.878741', '7.0.4', '11B554a', ''), ('6', '1', '2017-02-23 20:27:05.722476', '7.0.5', '11B601', ''), ('7', '1', '2017-02-23 20:27:14.824492', '7.0.6', '11B651', ''), ('8', '1', '2017-02-23 20:27:41.058626', '7.1', '11D167/11D169', ''), ('9', '1', '2017-02-23 20:27:50.743600', '7.1.1', '11D201', ''), ('10', '1', '2017-02-23 20:27:59.778728', '7.1.2', '11D257', ''), ('11', '1', '2017-02-23 20:28:22.121619', '8.0', '12A365/12A366', ''), ('12', '1', '2017-02-23 20:28:37.962418', '8.0.1', '12A402', ''), ('13', '1', '2017-02-23 20:28:47.220831', '8.0.2', '12A405', ''), ('14', '1', '2017-02-23 20:29:09.496014', '8.1', '12B410/12B411', ''), ('15', '1', '2017-02-23 20:29:31.951212', '8.1.1', '12B435/12B436', ''), ('16', '1', '2017-02-23 20:29:41.245193', '8.1.2', '12B440', ''), ('17', '1', '2017-02-23 20:29:49.558666', '8.1.3', '12B466', ''), ('18', '1', '2017-02-23 20:30:01.607079', '8.2', '12D508', ''), ('19', '1', '2017-02-23 20:30:22.195267', '8.3', '12F69/12F70', ''), ('20', '1', '2017-02-23 20:30:34.750614', '8.4', '12H143', ''), ('21', '1', '2017-02-23 20:30:48.858743', '8.4.1', '12H321', ''), ('22', '1', '2017-02-23 20:31:10.043252', '9.0', '13A340/13A342/13A343/13A344', ''), ('23', '1', '2017-02-23 20:31:25.447806', '9.0.1', '13A404/13A405', ''), ('24', '1', '2017-02-23 20:31:35.242925', '9.0.2', '13A452', ''), ('25', '1', '2017-02-23 20:31:46.694711', '9.1', '13B143', ''), ('26', '1', '2017-02-23 20:32:00.588886', '9.2', '13C75', ''), ('27', '1', '2017-02-23 20:32:14.842875', '9.2.1', '13D15/13D20', ''), ('28', '1', '2017-02-23 20:32:38.918867', '9.3', '13E233/13E234/13E236/13E237', ''), ('29', '1', '2017-02-23 20:32:52.486621', '9.3.1', '13E238', ''), ('30', '1', '2017-02-23 20:33:01.981245', '9.3.2', '13F69/13F72', ''), ('31', '1', '2017-02-23 20:33:10.812760', '9.3.3', '13G34', ''), ('32', '1', '2017-02-23 20:33:18.732530', '9.3.4', '13G35', ''), ('33', '1', '2017-02-23 20:33:25.798013', '9.3.5', '13G36', ''), ('34', '1', '2017-02-23 20:34:16.648571', '10.0', '14A346', ''), ('35', '1', '2017-02-23 20:34:23.140254', '10.0.1', '14A403', ''), ('36', '1', '2017-02-23 20:34:36.279151', '10.0.2', '14A456', ''), ('37', '1', '2017-02-23 20:34:43.053013', '10.0.3', '14A551', ''), ('38', '1', '2017-02-23 20:34:55.708453', '10.1', '14B72/14B72c', ''), ('39', '1', '2017-02-23 20:35:17.208134', '10.1.1', '14B100/14B150', ''), ('40', '1', '2017-02-23 20:35:28.518381', '10.2', '14C92', ''), ('41', '1', '2017-02-23 20:35:38.504536', '10.2.1', '14D27', '');"
        ),
    ]
