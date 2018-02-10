# -*- coding:utf-8 -*-


class Config(object):
    DEBUG = True
    SECRET_KEY = '&UhNe97#eYTsnpLSwq@#&yHdj39eDfr'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:21ops.com@localhost/ws_ts_sys'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # 分页配置
    LINES_PER_PAGE = 10
    SWITCHS_PER_PAGE = 10
    AREAS_PER_PAGE = 10
    IPADDRS_PER_PAGE = 10
    CERS_PER_PAGE = 10
    USERS_PER_PAGE = 10

    # celery配置
    CELERY_BROKER_URL = 'redis://localhost:6379/0',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_TIMEZONE = 'Asia/Shanghai'

    # redis配置
    REDIS_URL = "redis://localhost:6379/2"

    @staticmethod
    def init_app(app):
        pass
