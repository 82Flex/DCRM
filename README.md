<p align="center">
  <img src="https://raw.githubusercontent.com/82Flex/DCRM/master/docs/logo.png" width="160"/><br />
</p>
<p align="center">DCRM - Darwin Cydia Repository Manager (Version 4)</p>


## WARNING 警告

DO NOT USE DCRM FOR DISTRIBUTING PIRATED PACKAGES.

禁止将 DCRM 用于**分发盗版软件包**。根据开源许可，任何对源码的更改均需要向实际用户提供修改后的源码（包括网络分发、在线服务）。

请在使用 DCRM 前请务必仔细阅读并透彻理解开源许可与使用协议，您的任何使用行为将被视为对本项目开源许可和使用协议中全部内容的认可，否则您无权使用本项目。任何违反开源许可及使用协议的行为将被记入耻辱柱中并保留追究法律责任的权力。


## TODOs 计划任务

- pdiff
- Restful API
- Plugins


## GUIDE 使用说明


### DEMO SITE 示例站点

- https://apt.uozi.org


### ENVIRONMENT 基本环境

- Python 2.7
- Django 1.10.5 final
- Redis (Recommended)
- memcached (Recommended)
- MySQL / PostgreSQL
- uwsgi, Nginx


### CONFIGURATIONS 配置示例

git, nginx, mysql and python (pip)
Give a password of root to mysql.

```shell
apt-get update
apt-get upgrade
apt-get install git nginx mysql-server libmysqlclient-dev python-dev python-pip
```

python modules

```shell
pip install -r requirements.txt
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -D mysql -u root -p
```

If you want to enable Redis support:

```shell
apt-get install redis-server
pip install rq
```

If you want to enable Page Caching:

```shell
apt-get install memcached
pip install python-memcached
```

If you want to enable Screenshots:

```shell
apt-get install libjpeg-dev
pip install Pillow exifread
```

Then we log in to mysql:

```shell
mysql -uroot -p
```

Create a database for this DCRM instance:

```sql
CREATE DATABASE `DCRM` DEFAULT CHARSET UTF8;
```

Create user and grant privileges for it:

```sql
CREATE USER 'dcrm'@'localhost' IDENTIFIED BY 'thisisthepassword';
GRANT ALL PRIVILEGES ON `DCRM`.* TO 'dcrm'@'localhost';
FLUSH PRIVILEGES;
```

Clone this git repository:

```shell
cd /wwwdata
git clone https://github.com/82Flex/DCRM.git
cd /wwwdata/DCRM
```

Copy DCRM/settings.default.py to DCRM/settings.py and edit it:

    1. Set a random `SECRET_KEY`, it must be unique.
    2. Add your domain into `ALLOWED_HOSTS`.
    3. Configure Redis to match your redis configurations: `RQ_QUEUES`, you may use different 'DB' number for different DCRM instances.
    4. Configure Databases to match your mysql configurations: `DATABASES`, you may use different 'DATABASE' for different DCRM instances.
    5. Configure Caches to match your memcached configuration: `CACHES`.
    6. Configure Language & Timezone: `LANGUAGE_CODE` and `TIME_ZONE`.
    7. Set `DEBUG = True` in debug environment, set `DEBUG = False` in production environment.


Sync static files:

```shell
./manage.py collectstatic
```

Sync database structure and create new super user:

```shell
./manage.py migrate
./manage.py createsuperuser
```


#### CONFIGURE UWSGI 配置示例

By default, nginx uses `www-data` as its user and group.

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

To test:

```shell
uwsgi --ini uwsgi.ini
```

To run:

```shell
uwsgi --ini uwsgi.ini --daemonize=/dev/null
```


#### CONFIGURE NGINX 配置示例

This is the configuration of 82Flex Repo, with SSL.

```nginx
upstream django {
    server 127.0.0.1:8001;  # to match your uwsgi configuration
}
server {
    listen 80;
    server_name apt.82flex.com;  # your domain
    rewrite ^/(.*)$ https://apt.82flex.com/$1 permanent;  # redirect to https
}
server {
    listen 443 ssl;

    ssl_certificate /wwwdata/ssl/1_apt.82flex.com_bundle.crt;  # your ssl cert
    ssl_certificate_key /wwwdata/ssl/2_apt.82flex.com.key;  # your ssl key
    ssl_session_timeout 5m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers "EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5";
    ssl_prefer_server_ciphers on;

    server_name apt.82flex.com;  # your domain
    root /wwwdata/wwwroot;  # specify a web root, not the DCRM directory
    error_page 497 https://$host$uri?$args;
    server_name_in_redirect off;
    index index.html index.htm;
    
    location = / {
        # only enable this section if you want to use DCRM as your home page
        rewrite ^ /index/ last;
    }
    
    location / {
        # only enable this section if you want to use DCRM as your default pages
        try_files $uri $uri/ @djangosite;
    }	
    
    location ~^/static/(.*)$ {
        # static files for DCRM, you can change its path in settings.py
        alias /wwwdata/DCRM/WEIPDCRM/static/$1;  # make an alias for static files
    }

    location ~^/resources/(.*)$ {
        # resources for DCRM, including debian packages and icons, you can change it in WEIPDCRM > Settings in admin panel
        alias /wwwdata/DCRM/resources/$1;  # make an alias for resources
        
        # Aliyun CDN/OSS:
        # you can mount '/wwwdata/DCRM/resources' to oss file system
        # then rewrite this path to oss/cdn url for a better performance
    }
    
    location ~^/((CydiaIcon.png)|(Release(.gpg)?)|(Packages(.gz|.bz2)?))$ {
        # Cydia meta resources, including Release, Release.gpg, Packages and CydiaIcon
        alias /wwwdata/DCRM/resources/releases/1/$1;  # make an alias for Cydia meta resources
    }
    
    location @djangosite {
        uwsgi_pass django;
        include /etc/nginx/uwsgi_params;
    }
    
    location ~* .(ico|gif|bmp|jpg|jpeg|png|swf|js|css|mp3|m4a|m4v|mp4|ogg|aac)$ {
        expires 7d;
    }
    
    location ~* .(gz|bz2)$ {
        expires 12h;
    }
}
```


#### LAUNCH NGINX 启动

Test configuration:

```shell
nginx -t
```

Reload configuration:

```shell
nginx -s reload
```

Launch nginx if it is down:

```shell
sudo /etc/init.d/nginx start
```


#### LAUNCH BACKGROUND QUEUE (only if Redis Queue is enabled) 启动后台队列进程

Make sure to launch background queue with the same nginx working user (www/www-data).

```shell
su www-data
```

If you cannot switch to user `www-data`, remember to change its login prompt in `/etc/passwd`.
Launch some workers for DCRM background queue:

```shell
nohup ./manage.py rqworker high > /dev/null &
nohup ./manage.py rqworker default > /dev/null &
```


#### CONFIGURE GnuPG (only if GnuPG is enabled) 配置示例

```shell
apt-get install gnupg2
```

Make sure to launch background queue with the same nginx working user (www/www-data).

```shell
su www-data
```

```shell
gpg --gen-key
# or
gpg --allow-secret-key-import --import private.key
```


### Update DCRM 更新示例

```shell
git pull
./manage.py migrate
rm -rf WEIPDCRM/static
./manage.py collectstatic
killall -s INT uwsgi
uwsgi --ini uwsgi.ini
```


#### PUBLISH A REPOSITORY RELEASE 发布软件源

1. Sites: Set domains and site names
2. WEIPDCRM -> Settings
3. WEIPDCRM -> Releases: Add a new release and set it as an active release
4. WEIPDCRM -> Sections: Add sections
5. Upload: Upload deb files
6. WEIPDCRM -> Versions: Enable Packages and assign them into sections
7. WEIPDCRM -> Builds: Build the repository to apply all the changes


## LICENSE 版权声明

Copyright © 2013-2017 Zheng Wu
    
The program is distributed under the terms of the GNU Affero General Public License.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
