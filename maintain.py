# coding=utf-8

"""
DCRM - Darwin Cydia Repository Manager
Copyright (C) 2017  WU Zheng <i.82@me.com> & 0xJacky <jacky-943572677@qq.com>

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

import argparse
import commands
import os

parser = argparse.ArgumentParser(description='DCRM Maintenance Script')
parser.add_argument('-s', '--start', action="store", default=None, help='{rqworker|uwsgi}')
parser.add_argument('-r', '--restart', action="store", default=None, help='{rqworker|uwsgi}')
parser.add_argument('-u', '--update', action="store_true", help='Updata DCRM automaticly')
args = parser.parse_args()


def start(process):
    if process == 'rqworker':
        ID = commands.getoutput("ps -def | grep \"rqworker\" | grep -v \"grep\" | awk '{print $2}'")
        if ID == '':
            high = os.system("nohup python manage.py rqworker high > /dev/null &")
            default = os.system("nohup python manage.py rqworker default > /dev/null &")

            if high == 0 and default == 0:
                print("Start rqworker succssed!")
            else:
                print("Start rqworker failed!")
        else:
            print("rqworker already running")
    elif process == 'uwsgi':
        ID = commands.getoutput("ps -def | grep \"dcrm\" | grep -v \"grep\" | awk '{print $2}'")
        if ID == '':
            uwsgi = os.system("uwsgi --ini dcrm.ini --daemonize=/dev/null")
            if uwsgi == 0:
                print("Start uwsgi succssed!")
            else:
                print("Start uwsgi failed!")
        else:
            print("Uwsgi already running")


def kill(process):
    ID = commands.getoutput("ps -def | grep \"rqworker\" | grep -v \"$0\" | grep -v \"grep\" | awk '{print $2}'")

    for id in ID.split():
        out = os.system('kill -9 ' + id)

        if out == 0:
            print("Kill "+process+" succssed!")
        else:
            print("Kill "+process+" failed!")

if args.start:
    p = args.start
    if p in ['rqworker', 'uwsgi']:
        start(p)

elif args.restart:
    p = args.restart
    if p in ['rqworker', 'uwsgi']:
        kill(p)
        start(p)

elif args.update:
    git = commands.getoutput("git pull")
    if git != "Already up to date.":
        os.system("rm -rf WEIPDCRM/static && python manage.py collectstatic --noinput")
        kill('uwsgi')
        start('uwsgi')
