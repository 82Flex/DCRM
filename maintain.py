#!/usr/bin/env python
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

from aliyunsdkcdn.request.v20141111 import RefreshObjectCachesRequest
from aliyunsdkcore import client  # run `pip install aliyun-python-sdk-cdn` to install aliyun sdk
from DCRM.settings import ALLOWED_HOSTS
import argparse
import subprocess
import os
import time
import json

env = os.environ
ak = env['AliyunAK'] if 'AliyunAK' in env else ''  # Aliyun Access Key ID
sk = env['AliyunSK'] if 'AliyunSK' in env else '' # Aliyun Access Key Secret

parser = argparse.ArgumentParser(description='DCRM maintenance script')
parser.add_argument('-s', '--start', action="store", default=None, help='{rqworker|uwsgi}')
parser.add_argument('-r', '--restart', action="store", default=None, help='{rqworker|uwsgi}')
parser.add_argument('-c', '--clean', action="store", default=None, help='clean {memcached|cdn} cache')
parser.add_argument('-u', '--update', action="store_true", help='update DCRM automatically')
args = parser.parse_args()


def get_process_id(name):
    ID = subprocess.getoutput("ps -def | grep \"" + name + "\" | grep -v \"grep\" | awk '{print $2}'")
    return ID.split()


def start(process):
    if process == 'rqworker':
        if get_process_id(process):
            high = os.system("nohup python manage.py rqworker high > /dev/null &")
            default = os.system("nohup python manage.py rqworker default > /dev/null &")
            if high == 0 and default == 0:
                print("start rqworker successed.")
            else:
                print("start rqworker failed.")
        else:
            print("rqworker already running")
    elif process == 'uwsgi':
        if get_process_id(process):
            uwsgi = os.system("uwsgi --ini dcrm.ini --daemonize=/dev/null")
            if uwsgi == 0:
                print("start uwsgi successed.")
            else:
                print("start uwsgi failed.")
        else:
            print("uwsgi already running")


def kill(process):
    for id in get_process_id('rqworker'):
        out = os.system('kill -9 ' + id)
        if out == 0:
            print("kill " + process + " successed.")
        else:
            print("kill " + process + " failed.")


def flush_memcached():
    clean = subprocess.getoutput("echo \"flush_all\" | nc localhost 11211")
    if clean.strip() == 'OK':
        print("Flush Memcached successed.")
    else:
        print("Flush Memcached failed.")


def refresh_cdn():
    if ak and sk:
        try:
            Client = client.AcsClient(ak, sk, 'cn-hangzhou')
            request = RefreshObjectCachesRequest.RefreshObjectCachesRequest()
            request.set_accept_format('json')
            request.set_ObjectPath(ALLOWED_HOSTS[0]+'/static/')
            request.set_ObjectType('Directory')
            RequestId = json.loads(Client.do_action_with_exception(request))['RequestId']
            print("Refresh success\nRequestId: " + RequestId)

        except Exception as e:
            print(e.get_error_code() if hasattr(e, 'get_error_code') else e)


if args.start:
    p = args.start
    if p in ['rqworker', 'uwsgi']:
        start(p)

elif args.restart:
    p = args.restart
    if p in ['rqworker', 'uwsgi']:
        kill(p)
        time.sleep(3)
        start(p)

elif args.update:
    git = subprocess.getoutput("git pull")
    os.system("rm -rf WEIPDCRM/static && python manage.py collectstatic --noinput")
    kill('uwsgi')
    time.sleep(3)
    start('uwsgi')
    flush_memcached()
    refresh_cdn()

elif args.clean:
    if args.clean == 'cdn':
        refresh_cdn()
    elif args.clean == 'memcached':
        flush_memcached()
    else:
        print('Unknown command')
