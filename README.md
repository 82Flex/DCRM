<p align="center">
  <img src="https://raw.githubusercontent.com/82Flex/DCRM/master/docs/logo.png" width="160"/><br />
</p>
<p align="center">DCRM - Darwin Cydia Repository Manager (Version 4)</p>

## WARNING 警告

DO NOT USE DCRM FOR DISTRIBUTING PIRATED PACKAGES.

禁止将 DCRM 用于**分发盗版软件包**。根据开源许可，任何对源码的更改均需要向实际用户提供修改后的源码（包括网络分发、在线服务）。

请在使用 DCRM 前请务必仔细阅读并透彻理解开源许可与使用协议，您的任何使用行为将被视为对本项目开源许可和使用协议中全部内容的认可，否则您无权使用本项目。任何违反开源许可及使用协议的行为将被记入耻辱柱中并保留追究法律责任的权力。

## GUIDE 使用说明

The initial version of DCRMv4 is now under the development, and for now, only English version is available. You can try it if you know how to use Django and test its project.

### DEMO SITE 示例站点

- https://apt.82flex.com

### ENVIRONMENT OF DCRM 的基本环境要求是什么？
- Python 2.7
- Django 1.10.5 final
- Redis (Required)
- memcached (Recommended)
- MySQL / PostgreSQL
- uwsgi, Nginx

### INSTALL 如何安装 DCRM？

5. 登录管理后台，配置 WEIPDCRM -> Settings
6. 配置 Sites, 将 example.com 修改为当前域名，example 修改为软件源名称
7. 配置 WEIPDCRM -> Releases 源信息
8. 通过 Upload 上传 Deb 文件
9. 通过 WEIPDCRM -> Versions 启用并管理包
10. 通过 WEIPDCRM -> Sections 管理分类
11. 通过 WEIPDCRM -> Builds 发布源信息

### CONFIGURATIONS 配置示例

#### INSTALL MIDDLEWARES 环境配置指令示例

```shell
apt-get update
apt-get upgrade
```

```shell
apt-get install mysql-server libmysqlclient-dev python-dev memcached nginx git redis-server libjpeg-dev
```

```shell
pip install django==1.10.5 chardet rq bzip2 mysql sqlparse python-memcached uwsgi Pillow pytz python-debian --upgrade
```

```shell
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -D mysql -u root -p
```

#### CHECK PYPI PACKAGE VERSIONS 测试环境 python 包版本

```shell
pip freeze
```

Check the PyPI package versions to avoid any problem.

```shell
appdirs==1.4.3
bzip2==0.0.1
chardet==2.3.0
click==6.7
Django==1.10.5
ExifRead==2.1.2
mysql==0.0.1
MySQL-python==1.2.5
olefile==0.44
packaging==16.8
Pillow==4.0.0
pyparsing==2.2.0
python-debian==0.1.28
python-memcached==1.58
pytz==2016.10
redis==2.10.5
rq==0.7.1
six==1.10.0
sqlparse==0.2.3
uWSGI==2.0.14
```

#### CONFIGURE DATABASE MYSQL 配置示例

```shell
mysql -uroot -p
```

Create different databases for each DCRM instance.

```sql
CREATE DATABASE DCRM DEFAULT CHARSET UTF8;
```

#### CONFIGURE DCRM 配置示例

```shell
git clone https://github.com/82Flex/DCRM.git
cd DCRM
```

修改 DCRM/settings.py:
Edit DCRM/settings.py:
    1. Set SECRET_KEY, it must be unique.
    2. Add your domain into ALLOWED_HOSTS
    3. Configure Redis: RQ_QUEUES, you may use different 'DB' number for different DCRM instances.
    4. Configure Database: DATABASES, you may use different 'DATABASE' for different DCRM instances.
    5. Configure Caches: CACHES
    6. Configure Language & Timezone: LANGUAGE_CODE、TIME_ZONE
    7. Set Debug = True

执行下列语句，以创建数据库结构并创建超级用户：
Execute following commands to sync database structure and create new super user:

```shell
./manage.py collectstatic
./manage.py migrate
./manage.py createsuperuser
```

每次更新时，请执行下列语句：
Each time when you want to update DCRM, you should execute following commands:

```shell
git pull
./manage.py migrate
killall -s INT uwsgi
uwsgi --ini uwsgi.ini
```

#### CONFIGURE NGINX 配置示例

This is the configuration of 82Flex Repo, with SSL.

```nginx
upstream django {
    server 127.0.0.1:8001; 
}
server {
    listen 80;
    server_name apt.82flex.com;
    rewrite ^/(.*)$ https://apt.82flex.com/$1 permanent;
}
server {
    listen 443 ssl;

    ssl_certificate /wwwdata/ssl/1_apt.82flex.com_bundle.crt;
    ssl_certificate_key /wwwdata/ssl/2_apt.82flex.com.key;
    ssl_session_timeout 5m;
    ssl_protocols SSLv2 SSLv3 TLSv1;
    ssl_ciphers ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP;
    ssl_prefer_server_ciphers on;

    server_name apt.82flex.com;
    root /wwwdata/wwwroot;
    error_page 497 https://$host$uri?$args;
    server_name_in_redirect off;
    index index.html index.htm;
    
    location = / {
        rewrite ^ /index/ last;
    }
    
    location / {
        try_files $uri $uri/ @djangosite;
    }	
    
    location ~^/static/(.*)$ {
        alias /wwwdata/DCRM/WEIPDCRM/static/$1;
    }

    location ~^/resources/(.*)$ {
        alias /wwwdata/DCRM/resources/$1;
    }
    
    location ~^/((Release(.gpg)?)|(Packages(.gz|.bz2)?))$ {
        alias /wwwdata/DCRM/resources/releases/$1;
    }
    
    location @djangosite {
        uwsgi_pass django;
        include /etc/nginx/uwsgi_params;
    }
    
    location ~* .(ico|gif|bmp|jpg|jpeg|png|swf|js|css|mp3|m4a|m4v|mp4|ogg|aac)$ {
        expires 30d;
        valid_referers none blocked *.82flex.com 127.0.0.1 localhost;
        if ($invalid_referer) {
            return 403;
        }
    }
}
```

#### LAUNCH NGINX

```shell
sudo /etc/init.d/nginx start
```

#### CONFIGURE UWSGI 配置示例

```ini
[uwsgi]

chdir = /wwwdata/DCRM
module = DCRM.wsgi

master = true
processes = 4
socket = :8001
vaccum = true
uid = www-data
gid = www-data
```

#### LAUNCH UWSGI 启动 UWSGI

```shell
uwsgi --ini uwsgi.ini --daemonize=/dev/null
```

#### CONFIGURE GnuPG 配置示例

Make sure to launch background queue with the same nginx working user (www/www-data).

```shell
su www-data
```

```shell
gpg --gen-key
# or
gpg --allow-secret-key-import --import private.key
```

#### LAUNCH BACKGROUND QUEUE 启动后台队列进程

Make sure to launch background queue with the same nginx working user (www/www-data).

```shell
su www-data
```

```shell
nohup ./manage.py rqworker high > /dev/null &
nohup ./manage.py rqworker default > /dev/null &
```

## LICENSE 版权声明

Copyright © 2013-2017 Zheng Wu
    
The program is distributed under the terms of the GNU Affero General Public License.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
