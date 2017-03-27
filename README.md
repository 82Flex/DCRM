<p align="center">
  <img src="https://raw.githubusercontent.com/82Flex/DCRM/master/docs/logo.png" width="160"/><br />
</p>
<p align="center">DCRM - Darwin Cydia Repository Manager (Version 4)</p>

## WARNING 警告

DO NOT USE DCRM FOR DISTRIBUTING PIRATED PACKAGES.

禁止将 DCRM 用于**分发盗版软件包**。根据开源许可，任何对源码的更改均需要向实际用户提供修改后的源码（包括网络分发、在线服务）。

请在使用 DCRM 前请务必仔细阅读并透彻理解开源许可与使用协议，您的任何使用行为将被视为对本项目开源许可和使用协议中全部内容的认可，否则您无权使用本项目。任何违反开源许可及使用协议的行为将被记入耻辱柱中并保留追究法律责任的权力。

## GUIDE 使用说明

The initial version of DCRM is now under the development, and for now, only Chinese Installation Guideline is available. But DCRM is now in English, and you can try it if you know how to use Django and test its project.

### DCRM 的基本环境要求是什么？
- Python 2.7
- Django 1.10.5 final
- 如果您开启了此压缩方式，还需要额外的 bz2 模块
- 缓存：Redis (Required), memcached (Recommended)
- 关系型数据库：MySQL 或 PostgreSQL，无法使用 Django 自带的 SQLite3
- 在生产环境下强烈推荐您正确配置 uwsgi、Nginx 与 CDN 加速

### 如何安装 DCRM？
DCRM 尚处于开发阶段，暂不支持一键配置，请按照以下步骤进行部署：

1. 完成基本环境的配置
2. 配置 Nginx 或其它 Web 服务，将 resources 目录映射到站点可访问路径下，配置范例：https://github.com/82Flex/DCRM/blob/master/docs/example_nginx.conf
3. 设置 settings.py
    1. 设置随机 SECRET_KEY
    2. 将测试域名添加到 ALLOWED_HOSTS
    3. 配置 Redis：RQ_QUEUES
    4. 配置数据库：DATABASES
    5. 配置缓存：CACHES
    6. 配置语言及时区：LANGUAGE_CODE、TIME_ZONE
    7. Debug 置为 True 进行测试
4. 终端切换到本文件所在目录
    1. ./manage.py collectstatic
    2. ./manage.py migrate
    3. ./manage.py createsuperuser
    4. nohup ./manage.py rqworker high &
    5. nohup ./manage.py rqworker default &
5. 登录管理后台，配置 WEIPDCRM -> Settings
6. 配置 Sites, 将 example.com 修改为当前域名(e.g https://apt.82flex.com)，example 修改为软件源名称
7. 配置 WEIPDCRM -> Releases 源信息
8. 通过 Upload 上传 Deb 文件
9. 通过 WEIPDCRM -> Versions 启用并管理包
10. 通过 WEIPDCRM -> Sections 管理分类
11. 通过 WEIPDCRM -> Builds 发布源信息

### 如何开启 gpg 签名？
- 安装 gpg，然后在终端，**使用 rqworker 所在用户**执行 gpg --gen-key 生成密钥对。如服务器生成较慢，可在本地生成并在服务器上导入，即可开启 gpg 签名选项。此内容请参考：https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/4/html/Step_by_Step_Guide/s1-gnupg-export.html

### 如何配置下载次数统计或防盗链保护？
- Nginx 请参考：https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/

### 如何压缩传输页面尺寸？
- 安装 Django 扩展包：https://github.com/cobrateam/django-htmlmin/

### 如何让 DCRM 支持 emoji？
- 执行数据库语句，修改需要支持 emoji 字段的字符集：
- ALTER TABLE tbl_name CHANGE c_name c_name CHARACTER SET character_name [COLLATE ...];

### 出现 Permission Denied 如何解决？
- 请**让 rqworker 工作在 uwsgi 同一用户下**。例如 uwsgi 用户为 www，则启动 rqworker 时请采用 _sudo -u www nohup ./manage.py rqworker high &_。

### 配置示例

#### 环境配置指令示例

```shell
apt-get update
apt-get upgrade
apt-get install mysql-server libmysqlclient-dev python-dev memcached nginx git redis-server libjpeg-dev
pip install django==1.10.5 chardet rq mysql sqlparse python-memcached uwsgi Pillow python-debian --upgrade
```

#### 测试环境 python 包版本

```
appdirs==1.4.3
chardet==2.3.0
click==6.7
Django==1.10.5
django-photologue==3.6
django-sortedm2m==1.3.3
ExifRead==2.1.2
mysql==0.0.1
MySQL-python==1.2.5
olefile==0.44
packaging==16.8
Pillow==4.0.0
pyparsing==2.2.0
python-debian==0.1.28
python-memcached==1.58
redis==2.10.5
rq==0.7.1
six==1.10.0
sqlparse==0.2.3
uWSGI==2.0.14
```

#### nginx 配置示例 (https://apt.82flex.com)

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

nginx 工作用户及组均为 www-data，启动 nginx：
```shell
sudo /etc/init.d/nginx start
```

#### uwsgi 配置示例

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

启动 uwsgi：
```shell
sudo -u www-data -g www-data uwsgi --ini uwsgi.ini --daemonize=/dev/null
```

#### GnuPG 配置示例
```shell
su www-data
gpg --gen-key / gpg --allow-secret-key-import --import private.key
```

#### 启动后台队列进程
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
