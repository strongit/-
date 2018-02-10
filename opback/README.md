# opback
[![Build Status](https://travis-ci.org/tecstack/opback.svg?branch=promise)](https://travis-ci.org/tecstack/opback) [![Coverage Status](https://coveralls.io/repos/tecstack/opback/badge.svg?branch=promise)](https://coveralls.io/r/tecstack/opback?branch=promise) [![Download Status](https://img.shields.io/badge/download-1024%2Fmonth-green.svg)](https://github.com/tecstack/opback/)


This is the first stage of Promise.


## Prerequests

* python 2.7
* git
* easy_install && pip
* pyenv && pyenv-virtualenv

[参考这里](http://promisejohn.github.io/2015/04/15/PythonDevEnvSetting/)

## Usage

### 基本用法

```bash
$ git clone https://github.com/tecstack/opback.git
$ git branch promise
$ cd opback
$ pip install -r requirements.txt
*(OSX10.10上PIL安装失败，需执行
 ln -s /usr/local/include/freetype2 /usr/local/include/freetype；   xcode-select --install)
*(centos7安装mysql-python失败，执行yum install python-devel mysql-devel)
$ python scripts/manager.py recreatedb
$ python runserver.py
```
出现如下提示表示运行正常：

```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
```

```bash
$ celery worker -B -A promise.eater.tasks.celery -s .data/celerybeat-schedule 
  -l debug --pidfile=celerybeat.pid -f .log/celerybeat.log &
```
出现如下提示表示后台任务启动正常：
```
 * [2016-08-05 20:04:47,554: INFO/Beat] beat: Starting...
 * [2016-08-05 20:04:47,585: INFO/MainProcess] Connected to sqla+sqlite:///.../celerydb.sqlite
 * [2016-08-05 20:04:47,644: WARNING/MainProcess] celery@localhost ready.
```

* 打开浏览器，访问："http://localhost:5000"
* 访问："http://localhost:5000/_add_numbers?a=1&b=1"

* 配置文件 config.py
* 测试时可重载配置文件：instance/config.py

### Dev时用到的一些命令：

```bash
$ git clone https://github.com/tecstack/opback.git
$ cd opback
$ flake8 # 检查语法合规性，参照业内PEP8规范
$ tox # 多环境自动化单元测试
$ nosetests -v --with-coverage --cover-package=promise --exe # 代码单元测试覆盖率
$ python runserver.py # 直接启动
$ python scripts/manager.py runserver # 通过manager启动
$ python scripts/manager.py shell # 通过shell调测，自动import app, db, models
$ python scripts/manager.py initdb # 初始化数据库: .data/app.db
$ python scripts/manager.py importdata # 导入数据: .data/data.sql -- > .data/app.db
$ python scripts/manager.py dropdb # 删除数据库: .data/app.db
$ python scripts/manager.py recreatedb # 删除并重新创建数据库和导入数据: .data/app.db
$ python scripts/manager.py db migrate # 修改models之后通过migrate检测模型变更
$ python scripts/manager.py db upgrade # 根据自动检测变化更新数据库
$ python scripts/manager.py db downgrade # 数据库版本降级
$ autopep8 src/tecstack/xxx.py # 自动根据PEP8规范输出修改正代码
$ autopep8 -i src/tecstack/xxx.py # 自动根据PEP8规范修正代码，不会调整单行长度等
```

## 开发中的规约：

* `pip freeze`生成目前python环境依赖的类库，推荐pyenv独立环境（flask）内导出依赖库。
* `gitchangelog`生成git提交记录，由发布者写入changelog发布。
* `flake8`检查当前所写python的语法合规性，于业内规范PEP8做校验对比，不能有错误提示。
* `nosetests -v --with-coverage --cover-package=promise`执行单元测试，\
    要求通过所有写的测试，测试覆盖率80%以上。
* `tox`自动创建独立的python运行环境，并在每个独立环境内执行语法、单元测试任务，用于自动集成。
* 所有代码 **本地** 提交之前建议通过flake8和nosetests检查错误，无误后可以提交到本地仓库。
* 所有代码 **远程** 提交之前必须通过tox测试，无误后可以push到远程develop分支。
* **Never** use manager.py to do database operation in **Production Environment**.
* 单元测试中数据库采用.data/test.db，每个测试用例都会重新创建数据库
* **首次启动** 请使用manager初始化数据库并导入数据，待导入文件默认为data.sql，请确保其在.data目录下。

## 以下为promise branch新增规约：

* api与model隔离，在api中不import db，所有db操作封装在model中
* import包或类时，对当前目录采用“.”，上一级目录采用“..”，以此类推
* 单一配置文件

## 接口列表：
* 用户登录
```
method:POST 
URI:/api/v0.0/user/login
Params:[JSON]username,password(密码加密)
Return:[JSON]token,refreshtoken,message
```
* 令牌登录
```
method:POST
URI:/api/v0.0/user/tokenauth
Params:[HEADER]token
Return:[JSON]message
```
* 令牌更新
```
method:POST
URI:/api/v0.0/user/tokenrefresh
Params:[body-JSON]granttype,refreshtoken
Return:[body-JSON]token,message
```
* 用户列表
```
method:GET
URI:/api/v0.0/user
Params:[HEADER]token
Return:[body-JSON]usr_infos
```
* 单用户信息
```
method:GET
URI:/api/v0.0/user
Params:[HEADER]token,[url-param]userid
Return:[body-JSON]usr_infos
```