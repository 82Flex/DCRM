<p align="center">
  <img src="https://raw.githubusercontent.com/82Flex/DCRM/master/docs/logo.png" width="160"/><br />
</p>
<p align="center">DCRM - Darwin Cydia Repository Manager (Version 4)</p>
<p align="center">DO NOT USE DCRM FOR DISTRIBUTING PIRATED PACKAGES. 请勿使用 DCRM 分发盗版软件包.</p>


<!-- TOC insertanchor:true -->

- [SUMMARY](#summary)
    - [Features](#features)
    - [TODOs](#todos)
- [DEMO](#demo)
- [DOCKER DEPLOY 自动部署 (Docker)](#docker-deploy-自动部署-docker)
    - [DOCKER COMMANDS 常用命令](#docker-commands-常用命令)
    - [Configure GnuPG](#configure-gnupg)
- [PUBLISH REPOSITORY 发布软件源](#publish-repository-发布软件源)
- [MANUALLY DEPLOY 手动部署](#manually-deploy-手动部署)
    - [ENVIRONMENT 环境](#environment-环境)
    - [EXAMPLE 示例](#example-示例)
    - [IN PRODUCTION 生产环境示例](#in-production-生产环境示例)
        - [Configure UWSGI](#configure-uwsgi)
        - [UWSGI Commands](#uwsgi-commands)
        - [Configure NGINX](#configure-nginx)
        - [NGINX Commands](#nginx-commands)
        - [Configure Workers](#configure-workers)
        - [Configure GnuPG](#configure-gnupg)
- [LICENSE 版权声明](#license-版权声明)

<!-- /TOC -->


----


# 1. SUMMARY
<a id="markdown-summary" name="summary"></a>

DCRM means Darwin Cydia Repo (APT) Manager, which is designed for [Jay Freeman](https://twitter.com/saurik)'s [Cydia](https://en.wikipedia.org/wiki/Cydia). Cydia is an universal package manager for jailbroken devices.


## 1.1. Features
<a id="markdown-features" name="features"></a>

- full featured dashboard powered by Django and Django Suit
- restful APIs with full documentation powered by Django REST framework
- import Debian package (.deb) via http upload
- manage packages, versions, sections and icons
- sync control fields between db and the `control` file inside package automatically
- auto generated depiction pages, mobile optimized
- threaded comments & screenshots gallery
- iOS version / product type compatibility check
- version history & downgrade support
- download count & statistics
- scheduled tasks
- multiple users / groups
- CDN/OSS friendly
- GPG signature
- supports Docker


## 1.2. TODOs
<a id="markdown-todos" name="todos"></a>

- apt pdiff feature
- support for commercial packages
- import package via ftp upload
- more themes


# 2. DEMO
<a id="markdown-demo" name="demo"></a>

This demo is deployed using [Container Optimized OS](https://cloud.google.com/community/tutorials/docker-compose-on-container-optimized-os) on Google Cloud.

[https://apt.82flex.com/](https://apt.82flex.com/)

* Username: `root`
* Password: `dcrmpass`

Before you build your personal Cydia repository, watch this guide video:[https://youtu.be/dvNCRckm2Cc](https://youtu.be/dvNCRckm2Cc)


# 3. DOCKER DEPLOY 自动部署 (Docker)
<a id="markdown-docker-deploy-自动部署-docker" name="docker-deploy-自动部署-docker"></a>

以下步骤能完整部署 DCRM 最新副本, 启用了任务队列及页面缓存支持, 你可以根据需要调整自己的配置.

1. download this project or clone this git repo:
如果你还没有下载此项目, 建议使用 `git` 克隆该仓库:

```bash
git clone --depth 1 https://github.com/82Flex/DCRM.git && cd DCRM
```

2. build and launch DCRM via `docker-compose`
构建并启动 DCRM 容器:

```bash
docker-compose up --build --detach
```

3. attach to `dcrm_app` container:
先附加到容器中:

```bash
docker exec -i -t dcrm_app_1 /bin/bash
```

4. in container:
在容器中执行命令:

```bash
# collect static files
python manage.py collectstatic

# create required database structures
python manage.py migrate

# create super user in database
python manage.py createsuperuser
```

5. access admin panel via `http://127.0.0.1:8080/admin/`
现在可以尝试访问 DCRM 后台了


## 3.1. DOCKER COMMANDS 常用命令
<a id="markdown-docker-commands-常用命令" name="docker-commands-常用命令"></a>

1. build then launch DCRM in background (when app src code updated) 重新构建并在后台启动 DCRM (仅当代码发生变动, 不会影响数据)

```bash
docker-compose up --build --detach
```

2. launch DCRM in background only 仅在后台启动 DCRM

```bash
docker-compose up --detach
```

3. shutdown DCRM 停止 DCRM

```bash
docker-compose down
```


## 3.2. Configure GnuPG
<a id="markdown-configure-gnupg" name="configure-gnupg"></a>

1. attach to `dcrm_app` container:

```bash
docker exec -i -t dcrm_app_1 /bin/bash
```

2. generate new GPG key:

```bash
gpg --gen-key --homedir .gnupg
# or
gpg --allow-secret-key-import --import private.key --homedir .gnupg
```

3. enable GPG feature and configure passphrase in `WEIPDCRM -> Settings -> Security`
4. create APT verification package in `WEIPDCRM -> Sections -> Action -> Generate icon package for selected sections`, which will install GPG public key to user's device


# 4. PUBLISH REPOSITORY 发布软件源
<a id="markdown-publish-repository-发布软件源" name="publish-repository-发布软件源"></a>

Before you publish your repository, there are a few steps you should follow:
部署完成后, 你还需要一些步骤来发布你的软件源:

1. `Sites`

Set domains and site names.
在 Sites 中设置域名和站点名称

2. `WEIPDCRM -> Settings`
3. `WEIPDCRM -> Releases`

Add a new release and set it as an active release.
添加新的 Release 并将其设置为活跃状态

4. `WEIPDCRM -> Sections`

Add sections.
添加源分类 (可以生成分类图标包)

5. `WEIPDCRM -> Versions -> Add Version`

Upload your debian package.
上传你的 deb 包

6. `WEIPDCRM -> Versions`

Enable package versions and assign them into sections.
记得启用你的 deb 包 (默认不启用), 并且将它们分配到源分类当中

7. `WEIPDCRM -> Builds`

Build the repository to apply all the changes, thus you cannot add this repo in Cydia.
构建全源, 让所有更改生效 (第一次构建前, Cydia 中是无法添加该源的)


# 5. MANUALLY DEPLOY 手动部署
<a id="markdown-manually-deploy-手动部署" name="manually-deploy-手动部署"></a>

## 5.1. ENVIRONMENT 环境
<a id="markdown-environment-环境" name="environment-环境"></a>

- gzip, bzip2, **xz (xz-devel)**
- Python 3.7 (*CentOS: if Python is compiled from source, make sure package `xz-devel` is installed*)
- Django 1.11+
- MySQL (or MariaDB)
- Redis (optional)
- memcached (optional)
- uwsgi, Nginx (production only)


## 5.2. EXAMPLE 示例
<a id="markdown-example-示例" name="example-示例"></a>

1. install dependencies:
安装依赖:

```bash
apt-get update
apt-get upgrade
apt-get install git mysql-server libmysqlclient-dev python3-dev python3-pip libjpeg-dev tzdata
```

2. configure mysql:
安装完成后, 登录到 mysql:

```bash
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

```bash
mkdir -p /wwwdata
cd /wwwdata
git clone --depth 1 https://github.com/82Flex/DCRM.git
cd /wwwdata/DCRM
```

6. install python modules:
安装必要的 python 模块:

```bash
pip3 install -r requirements.txt
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -D mysql -u root -p
```

7. enable redis support (task queue):
如果你还需要开启 Redis 支持 (用于任务队列):

```bash
apt-get install redis-server
service redis-server start
```

8. enable memcached support (page caching):
如果你还需要开启页面缓存, 你可能还需要自行启动 memcached 服务:

```bash
apt-get install memcached
service memcached start
```

9. modify `DCRM/settings.py`:

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

```bash
python3 manage.py collectstatic
```

11. migrate database and create new super user:
同步数据库结构并创建超级用户:

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

12. run debug server:
启动测试服务器:

```bash
python3 manage.py runserver
```

13. access admin panel via `http://127.0.0.1:8000/admin/`


## 5.3. IN PRODUCTION 生产环境示例
<a id="markdown-in-production-生产环境示例" name="in-production-生产环境示例"></a>

生产环境的配置需要有一定的服务器运维经验, 如果你在生产环境的配置过程中遇到困难, 我们提供付费的疑难解答.

We assumed that nginx uses `www-data` as its user and group.
假设 nginx 使用 `www-data` 用作其用户名和用户组名.


### 5.3.1. Configure UWSGI
<a id="markdown-configure-uwsgi" name="configure-uwsgi"></a>

here is an example of `uwsgi.ini`:

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
safe-pidfile = /home/run/uwsgi-apt.pid
; daemonize = /dev/null
```


### 5.3.2. UWSGI Commands
<a id="markdown-uwsgi-commands" name="uwsgi-commands"></a>

test:

```bash
uwsgi --ini uwsgi.ini
```

run:

```bash
uwsgi --ini uwsgi.ini --daemonize=/dev/null
```

kill:

```bash
kill -INT `cat /home/run/uwsgi-apt.pid`
```


### 5.3.3. Configure NGINX
<a id="markdown-configure-nginx" name="configure-nginx"></a>

here is an example of nginx https site configuration file:

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
    index index.html;
    
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


### 5.3.4. NGINX Commands
<a id="markdown-nginx-commands" name="nginx-commands"></a>

1. install Nginx:

```bash
apt-get install nginx
```

2. launch Nginx:

```bash
service nginx start
```

3. test configuration:

```bash
nginx -t
```

4. reload configuration:

```bash
nginx -s reload
```

5. launch nginx if it is down:

```bash
sudo /etc/init.d/nginx start
```


### 5.3.5. Configure Workers
<a id="markdown-configure-workers" name="configure-workers"></a>

make sure to launch task queue with the same nginx working user (www/www-data).

```bash
su www-data
```

if you cannot switch to user `www-data`, remember to change its login prompt in `/etc/passwd`. launch some workers for DCRM background queue:

```bash
nohup ./manage.py rqworker high > /dev/null &
nohup ./manage.py rqworker default > /dev/null &
```

you need at least one worker for each queue. worker 的数量以你的具体需求为准, 但是各队列中至少要有一个活跃 worker, 否则队列中的任务将一直保持挂起.


### 5.3.6. Configure GnuPG
<a id="markdown-configure-gnupg" name="configure-gnupg"></a>

1. install `gnupg2`

```bash
apt-get install gnupg2
```

2. make sure to launch background queue with the same nginx working user (www/www-data):

```bash
su www-data
```

3. generate new GPG key

```bash
gpg --gen-key --homedir .gnupg
# or
gpg --allow-secret-key-import --import private.key --homedir .gnupg
```

4. enable GPG feature and configure passphrase in `WEIPDCRM -> Settings -> Security`
5. create APT verification package in `WEIPDCRM -> Sections -> Action -> Generate icon package for selected sections`, which will install GPG public key to user's device


# 6. LICENSE 版权声明
<a id="markdown-license-版权声明" name="license-版权声明"></a>

Copyright © 2013-2020 Zheng Wu <i.82@me.com>
    
The program is distributed under the terms of the GNU Affero General Public License.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

