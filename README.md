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

### DCRM 所需的 Python 扩展包有哪些？
- pip install django
- pip install rq
- pip install mysql
- pip install python-debian --upgrade
- pip install sqlparse
- pip install python-memcached

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
6. 配置 WEIPDCRM -> Releases 源信息
7. 通过 Upload 上传 Deb 文件
8. 通过 WEIPDCRM -> Versions 启用并管理包
9. 通过 WEIPDCRM -> Sections 管理分类
10. 通过 WEIPDCRM -> Builds 发布源信息

### 如何开启 gpg 签名？
- 安装 gpg，然后在终端执行 gpg --gen-key 生成密钥对，即可开启 gpg 签名选项。

### 如何配置下载次数统计或防盗链保护？
- Nginx 请参考：https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/

### 如何压缩传输页面尺寸？
- 安装 Django 扩展包：https://github.com/cobrateam/django-htmlmin/

### 如何让 DCRM 支持 emoji？
- 执行数据库语句，修改需要支持 emoji 字段的字符集：
- ALTER TABLE tbl_name CHANGE c_name c_name CHARACTER SET character_name [COLLATE ...];

### 出现 Permission Denied 如何解决？
- 请让 rqworker 工作在 uwsgi 同一用户组。例如 uwsgi 用户为 www，则启动 rqworker 时请采用 _sudo -u www nohup ./manage.py rqworker high &_。

## LICENSE 版权声明

Copyright © 2013-2017 Zheng Wu
    
The program is distributed under the terms of the GNU Affero General Public License.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
