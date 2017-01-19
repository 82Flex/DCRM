import os
import tarfile
import tempfile


class DebianPackage:
    def __init__(self, path):
        self.path = path
        self.version = ""
        self.control = ""
        self.size = os.path.getsize(path)
        self.__load()

    def __load(self):
        has_flag = False
        has_control = False
        has_data = False
        # https://en.wikipedia.org/wiki/Deb_(file_format)
        fd = open(self.path, 'rb+')
        fd.seek(0)
        magic = fd.read(8)
        if magic != "!<arch>\n":
            raise IOError('Not a Debian Package')
        while True:
            is_flag = False
            is_control = False
            is_data = False
            identifier_d = fd.read(16).rstrip()
            if len(identifier_d) == 0:
                break
            elif identifier_d == 'debian-binary':
                self.has_flag = True
                is_flag = True
            elif identifier_d[:7] == 'control':
                self.has_control = True
                is_control = True
            elif identifier_d[:4] == 'data':
                self.has_data = True
                is_data = True
            timestamp_d = fd.read(12).rstrip()
            ownerID_d = fd.read(6).rstrip()
            groupID_d = fd.read(6).rstrip()
            mode_d = fd.read(8).rstrip()
            size_d = fd.read(10).rstrip()
            endc = fd.read(2)
            if endc != '`\n':
                raise IOError('Malformed Debian Package')
            size = int(size_d)
            if is_flag:
                if size != 4:
                    raise IOError('Malformed Debian Package')
                else:
                    self.version = fd.read(4).rstrip()
            elif is_control:
                control_data = fd.read(size)
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(control_data)
                temp.close()
                control_tar = tarfile.open(temp.name, "r")
                control_names = control_tar.getnames()
                if "./control" in control_names:
                    control_name = "./control"
                elif "control" in control_names:
                    control_name = "control"
                if control_name is None:
                    raise IOError('No Control Info')
                control_obj = control_tar.extractfile(control_name)
                control_content = control_obj.read()
                control_obj.close()
                control_tar.close()
                os.remove(temp.name)
                # http://man7.org/linux/man-pages/man5/deb-control.5.html
                required_cols = ['Package', 'Version']
                recommended_cols = ['Maintainer', 'Description', 'Architecture']
                cydia_cols = [
                    'Name', 'Depiction', 'Author', 'Sponsor', 'Icon'
                ]
                known_cols = [
                    'Package', 'Version',
                    'Maintainer', 'Description', 'Architecture',
                    'Name', 'Depiction', 'Author', 'Sponsor', 'Icon',
                    'Section', 'Priority', 'Installed-Size', 'Essential',
                    'Build-Essential', 'Origin', 'Bugs', 'Homepage',
                    'Tag', 'Multi-Arch', 'Source', 'Subarchitecture',
                    'Kernel-Version', 'Installer-Menu-Item', 'Depends',
                    'Pre-Depends', 'Recommends', 'Suggests', 'Breaks',
                    'Conflicts', 'Replaces', 'Provides', 'Built-Using',
                    'Built-For-Profiles'
                ]
                control_arr = control_content.split('\n')
                control_dict = {}
                all_cols = []
                for control_line in control_arr:
                    line_col = control_line.find(':')
                    if control_line[:1] != ' ' and line_col > 0:
                        key = control_line[:line_col]
                        value = control_line[line_col + 1:].strip()
                        all_cols.append(key)
                        control_dict.update({key: value})
                    else:
                        control_dict['Description'] = control_dict['Description'] + control_line[1:]
                # Standard Check
                for required_col in required_cols:
                    if required_col not in all_cols:
                        raise IOError('Package missing required column: ' + required_col)
                for recommended_col in recommended_cols:
                    if recommended_col not in all_cols:
                        print('Package missing recommended column: ' + recommended_col)
                for cydia_col in cydia_cols:
                    if cydia_col not in all_cols:
                        print('Package missing Cydia column: ' + cydia_col)
                for all_col in all_cols:
                    if all_col not in known_cols:
                        print('Package has unknown column: ' + all_col)
                self.control = control_dict
            else:
                fd.seek(fd.tell() + size)
            if size % 2 == 1:
                fd.read(1)  # Even Padding
        if not (has_flag and has_control and has_data):
            raise IOError('Malformed Debian Package')
