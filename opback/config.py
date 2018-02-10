# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T, Leann Mak
# Email: shawntai.ds@gmail.com, leannmak@139.com
# This is the config file of global package of promise.

import os
basedir = os.path.abspath(os.path.dirname('..'))

"""
    database configuration
"""
# database access string setting, by default we use mysql
# for common using
SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/common'

# SQLALCHEMY_POOL_RECYCLE = 3600
# for eater:
SQLALCHEMY_BINDS = {
    'eater': 'mysql://root@127.0.0.1:3306/common'
}
# when testing, put your instance setting in instance/config.py to cover it
# SQLALCHEMY_DATABASE_URI = 'mysql://root:111111@192.168.182.50:3306/dev4test'

# ADVISE：create instance/config.py, your sqlite setting might like this:
# get some folders and dirs:
# import os
basedir = os.path.abspath(os.path.dirname('..'))
DB_FOLDER = os.path.join(basedir, '.data')
DB_FILE = 'app.db'
DB_SOURCEFILE = 'data.sql'
DB_FILEPATH = os.path.join(DB_FOLDER, DB_FILE)
DB_SOURCEFILEPATH = os.path.join(DB_FOLDER, DB_SOURCEFILE)
# config the sqlite acces URI:
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DB_FOLDER, DB_FILE)
SQLALCHEMY_POOL_RECYCLE = 5

"""
    log file configuration
"""
LOGGER_FOLDER = os.path.join(basedir, '.log')
LOGGER_FILE = os.path.join(LOGGER_FOLDER, 'debug.log')

"""
    encryption & auth configuration
"""
# encryption keys
SECRET_KEY = 'your SECRET_KEY'
# salt used by token generation
AUTH_SALT = 'your AUTH SALT'
# salt used by password md5 hash
PSW_SALT = 'your PSW SALT'
# token duration (in seconds), 2hours by default
TOKEN_DURATION = 7200  # in second
ACCESS_TOKEN_EXPIRATION = 3600  # in second
REFRESH_TOKEN_EXPIRATION = 86400  # in second
# root user default setting
DEFAULT_ROOT_USERNAME = 'admin'
DEFAULT_ROOT_PASSWORD = 'admin'

"""
    walker configuration
"""
WALKER_MISSION_TIMEOUT = 180  # in second
ROOT_SSH_KEY_FILE = os.path.join(basedir, '.ssh_key/root_id_rsa')
ADMIN_SSH_KEY_FILE = os.path.join(basedir, '.ssh_key/admin_id_rsa')

"""
    forward configuration
"""
FORWARD_LOGLEVEL = 'info'
FORWARD_LOGGER_FILE = os.path.join(LOGGER_FOLDER, 'forward.log')
FORWARD_TIMEOUT = 2
FORWARD_USERNAME = 'python_script'
FORWARD_USER_PRIVATE_KEY = os.path.join(
    basedir, '.ssh_key/forward_private_rsa')
FORWARD_USER_PUBLIC_KEY = os.path.join(basedir, '.ssh_key/forward_public_rsa')

"""
    zabbix access configuration
"""
# zabbix url
DEFAULT_ZABBIX_URL = 'http://192.168.182.150/zabbix'
# zabbix user info
DEFAULT_ZABBIX_USER_NAME = 'cloudlab'
DEFAULT_ZABBIX_PASSWORD = 'cloudlab'

"""
    celery configuration
"""
# use sqlalchemy as broker and resultset
SQLA = os.path.join(DB_FOLDER, 'celerydb.sqlite')
CELERY_BROKER_URL = 'sqla+sqlite:///%s' % SQLA
CELERY_RESULT_BACKEND = 'db+sqlite:///%s' % SQLA
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
CELERYBEAT_SCHEDULE_FILENAME = os.path.join(DB_FOLDER, 'celerybeat-schedule')
# CELERY_IGNORE_RESULT = True
# CELERY_TRACK_STARTED = True
# CELERY_REDIRECT_STDOUTS_LEVEL = 'DEBUG'

from celery import platforms
platforms.C_FORCE_ROOT = True

"""
    forward database configuration
"""
FORWARD_DB_USER = 'root'
FORWARD_DB_PASS = ''
FORWARD_DB_HOST = '127.0.0.1'
FORWARD_DB_PORT = 3306
FORWARD_DB_NAME = 'forward'
FORWARD_DB_TIMEOUT = 2
