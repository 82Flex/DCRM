<p align="center">
  <img src="https://raw.githubusercontent.com/82Flex/DCRM/master/docs/logo.png" width="160"/><br />
</p>
<p align="center">DCRM - Darwin Cydia Repository Manager (Version 4)</p>


## WARNING 警告

DO NOT USE DCRM FOR DISTRIBUTING PIRATED PACKAGES.

禁止将 DCRM 用于**分发盗版软件包**。根据开源许可，任何对源码的更改均需要向实际用户提供修改后的源码（包括网络分发、在线服务）。

请在使用 DCRM 前请务必仔细阅读并透彻理解开源许可与使用协议，您的任何使用行为将被视为对本项目开源许可和使用协议中全部内容的认可，否则您无权使用本项目。任何违反开源许可及使用协议的行为将被记入耻辱柱中并保留追究法律责任的权力。


## TODOs

- pdiffs
- rqscheduler supports 定时任务支持



## ENVIRONMENT 环境

- gzip, bzip2, **xz (xz-devel)**
- Python 3.7 (*CentOS: if Python is compiled from source, make sure package `xz-devel` is installed*)
- Django 1.11+
- MySQL (or MariaDB)
- Redis (optional)
- memcached (optional)
- uwsgi, Nginx (production only)


## MANUALLY INSTALL 手动安装

### EXAMPLE 示例

1. install dependencies:
安装依赖:

```shell
apt-get update
apt-get upgrade
apt-get install git mysql-server libmysqlclient-dev python3-dev python3-pip libjpeg-dev tzdata
```

2. configure MySQL:
安装完成后, 登录到 MySQL:

```shell
service mysql start
mysql_secure_installation
mysql -uroot -p
```

3. create a database for this DCRM instance:
新建 DCRM 数据库:

```sql
CREATE DATABASE `DCRM` DEFAULT CHARSET UTF8;
```

4. create user and grant privileges:
新建 dcrm 用户并设置密码:

```sql
CREATE USER 'dcrm'@'localhost' IDENTIFIED BY 'thisisthepassword';
GRANT ALL PRIVILEGES ON `DCRM`.* TO 'dcrm'@'localhost';
FLUSH PRIVILEGES;
```

5. clone this git repo:
在合适的位置克隆 DCRM:

```shell
mkdir -p /wwwdata
cd /wwwdata
git clone --depth 1 https://github.com/82Flex/DCRM.git
cd /wwwdata/DCRM
```

6. install python modules:
安装需要的 python 模块:

```shell
pip3 install -r requirements.txt
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -D mysql -u root -p
```

7. enable Redis support:
如果你还需要开启 Redis 支持 (用于任务队列):

```shell
apt-get install redis-server
service redis-server start
```

8. enable Page Caching support:
如果你还需要开启页面缓存, 你可能还需要自行启动 memcached 服务:

```shell
apt-get install memcached
service memcached start
```

9. edit DCRM/settings.py:
修改配置文件 DCRM/settings.py:

    1. set a random `SECRET_KEY`, which must be unique
    2. add your domain into `ALLOWED_HOSTS`
    3. configure Redis to match your redis configurations: `RQ_QUEUES`, you may use different 'DB' numbers across DCRM instances
    4. configure databases to match your mysql configurations: `DATABASES`, you may use different 'DATABASE' across DCRM instances
    5. configure caches to match your memcached configuration: `CACHES`
    6. configure language and timezone: `LANGUAGE_CODE` and `TIME_ZONE`
    7. set `DEBUG = True` for debugging, set `DEBUG = False` for production
    8. enable optional features: `ENABLE_REDIS`, `ENABLE_CACHE`, `ENABLE_API`

10. collect static files:
同步静态文件:

```shell
python3 manage.py collectstatic
```

11. migrate database and create new super user:
同步数据库结构并创建超级用户:

```shell
python3 manage.py migrate
python3 manage.py createsuperuser
```

12. run debug server:
启动测试服务器:

```shell
python3 manage.py runserver
```


#### IN PRODUCTION 生产环境示例

生产环境的配置需要有一定的服务器运维经验, 如果你在生产环境的配置过程中遇到困难, 我们提供付费的疑难解答.

We assumed that nginx uses `www-data` as its user and group.
假设 nginx 使用 `www-data` 用作其用户名和用户组名.


##### Configure UWSGI

在 DCRM 目录下创建 `uwsgi.ini`:

```shell
touch uwsgi.ini
```

```ini
[uwsgi]

chdir = /home/DCRM
module = DCRM.wsgi

master = true
processes = 4
enable-threads = true
threads = 2
thunder-lock = true
socket = :8001
vaccum = true
uid = www-data
gid = www-data
; daemonize = /dev/null
safe-pidfile = /home/run/uwsgi-apt.pid
```

##### UWSGI Commands

test:

```shell
uwsgi --ini uwsgi.ini
```

run:

```shell
uwsgi --ini uwsgi.ini --daemonize=/dev/null
```

kill:

```shell
kill -INT `cat /home/run/uwsgi-apt.pid`
```


##### Configure NGINX

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
        
        # Note:
        # 'releases/(\d)+/$1' should contain `active_release.id`, which is set in Settings tab.
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


##### NGINX Commands

1. install Nginx:

```shell
apt-get install nginx
```

2. launch Nginx:

```shell
service nginx start
```

3. test configuration:

```shell
nginx -t
```

4. reload configuration:

```shell
nginx -s reload
```

5. launch nginx if it is down:

```shell
sudo /etc/init.d/nginx start
```


##### Launch Workers

make sure to launch background queue with the same nginx working user (www/www-data).

```shell
su www-data
```

if you cannot switch to user `www-data`, remember to change its login prompt in `/etc/passwd`.
Launch some workers for DCRM background queue:

```shell
nohup ./manage.py rqworker high > /dev/null &
nohup ./manage.py rqworker default > /dev/null &
```

worker 的数量以你的具体需求为准, 但是各队列中至少要有一个活跃 worker, 否则队列中的任务将一直保持挂起.


##### Configure GnuPG

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


#### PUBLISH A REPOSITORY 发布软件源

Before you publish your repository, there are a few steps you should follow:

1. `Sites` Set domains and site names. 在 Sites 中设置域名和站点名称.
2. `WEIPDCRM -> Settings`
3. `WEIPDCRM -> Releases` Add a new release and set it as an active release. 添加新的 Release 并将其设置为活跃状态.
4. `WEIPDCRM -> Sections` Add sections. 添加源分类 (可以生成分类图标包).
5. `WEIPDCRM -> Versions -> Add Version` Upload your debian package. 上传你的 deb 包.
6. `WEIPDCRM -> Versions` Enable package versions and assign them into sections. 记得启用你的 deb 包 (默认不启用), 并且将它们分配到源分类当中.
7. `WEIPDCRM -> Builds` Build the repository to apply all the changes. 构建全源, 让所有更改生效 (第一次构建前, Cydia 中是无法添加该源的).


## LICENSE 版权声明

Copyright © 2013-2020 Zheng Wu <i.82@me.com>
    
The program is distributed under the terms of the GNU Affero General Public License.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

