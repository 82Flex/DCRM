# coding=utf-8
"""
Class Implementation: DebianPackage
"""

from __future__ import unicode_literals

import os
import time
import tarfile
import tempfile

from django.utils.translation import ugettext as _

from debian.deb822 import Deb822
from debian.copyright import parse_multiline, format_multiline


class DebianPackage(object):
    """
    Some adjustment to package: https://packages.debian.org/sid/python-debian
    Which is really helpful because in python-debian, Debfile is read-only.
    """
    
    def __init__(self, path):
        self.path = path
        self.version = ""
        self.control = {}
        self.size = os.path.getsize(path)
        self.offset_control = 0
        self.offset_data = 0
        self.load()
    
    def load(self):
        """
        Load offsets and control dict
        """
        has_flag = False
        has_control = False
        has_data = False
        # https://en.wikipedia.org/wiki/Deb_(file_format)
        fd = open(self.path, 'rb')
        fd.seek(0)
        magic = fd.read(8)
        if magic != "!<arch>\n":
            raise IOError(_('Not a Debian Package'))
        while True:
            is_flag = False
            is_control = False
            is_data = False
            identifier_d = fd.read(16).rstrip()
            if len(identifier_d) == 0:
                break
            elif identifier_d == 'debian-binary':
                has_flag = True
                is_flag = True
            elif identifier_d[:7] == 'control':
                has_control = True
                is_control = True
            elif identifier_d[:4] == 'data':
                has_data = True
                is_data = True
            # timestamp_d =
            fd.read(12).rstrip()
            # ownerID_d =
            fd.read(6).rstrip()
            # groupID_d =
            fd.read(6).rstrip()
            # mode_d =
            fd.read(8).rstrip()
            size_d = fd.read(10).rstrip()
            endc = fd.read(2)
            if endc != '`\n':
                raise IOError(_('Malformed Debian Package'))
            size = int(size_d)
            if is_flag:
                if size != 4:
                    raise IOError(_('Malformed Debian Package'))
                else:
                    self.version = fd.read(4).rstrip()
            elif is_control:
                self.offset_control = fd.tell() - 60
                control_data = fd.read(size)
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(control_data)
                temp.close()
                control_tar = tarfile.open(temp.name)
                control_names = control_tar.getnames()
                control_name = None
                if "./control" in control_names:
                    control_name = "./control"
                elif "control" in control_names:
                    control_name = "control"
                if control_name is None:
                    raise IOError('No Control Info')
                control_obj = control_tar.extractfile(control_name)
                
                # Using Deb822 to parse control
                # Decoded automatically
                control_dict = {}
                rfc822 = Deb822(control_obj)
                for (k, v) in rfc822.items():
                    control_dict[k] = v
                control_dict["Description"] = parse_multiline(control_dict["Description"])
                self.control = control_dict
                
                control_obj.close()
                control_tar.close()
                os.remove(temp.name)
            else:
                if is_data:
                    self.offset_data = fd.tell() - 60
                fd.seek(fd.tell() + size)
            if size % 2 == 1:
                fd.read(1)  # Even Padding
        if not (has_flag and has_control and has_data):
            raise IOError(_('Malformed Debian Package'))
    
    @staticmethod
    def value_for_field(field):
        """
        Parse info string like: i_82 <i.82@me.com>
        return its former part
        :param field: Info string
        :type field: str
        :return: Former Value
        :rtype: str
        """
        if field is None:
            return None
        lt_index = field.find('<')
        if lt_index > 0:
            gt_index = field.find('>', lt_index)
            if gt_index > 0:
                return field[:lt_index].strip()
            else:
                return field
        else:
            return field
    
    @staticmethod
    def detail_for_field(field):
        """
        Parse info string like: i_82 <i.82@me.com>
        return its latter part
        :param field: Info string
        :type field: str
        :return: Latter Value
        :rtype: str
        """
        if field is None:
            return None
        lt_index = field.find('<')
        if lt_index > 0:
            gt_index = field.find('>', lt_index)
            if gt_index > 0:
                return field[lt_index + 1:gt_index].strip()
            else:
                return ''
        else:
            return ''
    
    @staticmethod
    def get_control_content(control_dict):
        """
        :type control_dict: Dictionary
        :rtype: str
        :return: Control in RFC822 Format
        """
        # Using Deb822 to format control
        control_dict["Description"] = format_multiline(control_dict["Description"])
        rfc822 = Deb822(control_dict)
        return rfc822.dump(encoding="utf-8") + "\n"  # Just add a blank line and encode
    
    def save(self):
        """
        Save this deb file if you have replaced its control
        """
        control = self.control
        control_field = DebianPackage.get_control_content(control)
        temp_control = tempfile.NamedTemporaryFile(delete=False)
        temp_control.write(control_field.encode("utf-8"))
        temp_control.close()
        temp_control_gz = tempfile.NamedTemporaryFile(delete=False)
        temp_control_gz.close()
        control_tar = tarfile.open(temp_control_gz.name, "w:gz")
        control_tar.add(temp_control.name, "./control")
        control_tar.close()
        control_tar_size = int(os.path.getsize(temp_control_gz.name))
        os.unlink(temp_control.name)
        new_deb = tempfile.NamedTemporaryFile(delete=False)
        new_deb.write(
            b"\x21\x3C\x61\x72\x63\x68\x3E\x0A"  # 8
            b"\x64\x65\x62\x69\x61\x6E\x2D\x62"  # 16
            b"\x69\x6E\x61\x72\x79\x20\x20\x20"  # 24
        )
        new_deb.write(str(int(time.time())).ljust(12))
        new_deb.write(
            b"\x30\x20\x20\x20\x20\x20\x30\x20"  # 8
            b"\x20\x20\x20\x20\x31\x30\x30\x36"  # 16
            b"\x34\x34\x20\x20\x34\x20\x20\x20"  # 24
            b"\x20\x20\x20\x20\x20\x20\x60\x0A"  # 32
            b"\x32\x2E\x30\x0A\x63\x6F\x6E\x74"  # 40
            b"\x72\x6F\x6C\x2E\x74\x61\x72\x2E"  # 48
            b"\x67\x7A\x20\x20"  # 52
        )
        new_deb.write(str(int(time.time())).ljust(12))
        new_deb.write(
            b"\x30\x20\x20\x20\x20\x20\x30\x20"  # 8
            b"\x20\x20\x20\x20\x31\x30\x30\x36"  # 16
            b"\x34\x34\x20\x20"  # 20
        )
        new_deb.write(str(control_tar_size).ljust(10))
        new_deb.write(b"\x60\x0A")
        control_tar = open(temp_control_gz.name, "rb")
        control_tar.seek(0)
        while True:
            cache = control_tar.read(16 * 1024)  # 16k cache
            if not cache:
                break
            new_deb.write(cache)
        control_tar.close()
        if control_tar_size % 2 != 0:
            new_deb.write(b"\x0A")
        data_tar = open(self.path, "rb")
        data_tar.seek(self.offset_data)
        while True:
            cache = data_tar.read(16 * 1024)  # 16k cache
            if not cache:
                break
            new_deb.write(cache)
        data_tar.close()
        new_deb.close()
        os.unlink(self.path)
        os.rename(new_deb.name, self.path)
