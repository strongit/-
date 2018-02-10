# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the Global package of promise,
# holding flask app, restful api, sqlalchemy db, etc.
#

import os

from flask import Flask

# Main flask object
app = Flask(__name__, instance_relative_config=True)

# Config File:
# use the instance/config.py to cover the default config object.
# u can put some instance settings into the instance/config.py

app.config.from_object('config')
if os.path.isfile('/instance/config.py'):
    app.config.from_pyfile('config.py')

# Init The Api Obj
from flask.ext.restful import Api
api = Api(app)
# api = Api(app, errors=errors)

# Init The db Obj
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Init The ma Obj for Data Formatting
from flask.ext.marshmallow import Marshmallow
ma = Marshmallow(app)

# Init .data and .log Folder in root dir
if not os.path.exists(app.config['LOGGER_FOLDER']):
    os.mkdir(app.config['LOGGER_FOLDER'])
if 'DB_FOLDER' in app.config:
    if not os.path.exists(app.config['DB_FOLDER']):
        os.mkdir(app.config['DB_FOLDER'])

from . import utils
# init the logger obj
app.logger.addHandler(utils.handler)

# Config for cross domain access
from flask.ext.cors import CORS
cors = CORS(app)

from flask.ext.cachecontrol import (
    FlaskCacheControl,
    cache,
    cache_for,
    dont_cache)
flask_cache_control = FlaskCacheControl()
flask_cache_control.init_app(app)

# Init The Celery Obj
from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# what services u privide, import your packages or modules here
from . import user, zabber, eater, walker, ansiAdapter
# use 'assert' to quiet flake8
assert user
assert zabber
assert eater
assert walker
assert ansiAdapter
assert cache
assert cache_for
assert dont_cache
