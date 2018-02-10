# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import Config
from celery import Celery, platforms
from flask_redis import FlaskRedis

db = SQLAlchemy()
config = Config()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = None
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
redis_store = FlaskRedis()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    config.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    redis_store.init_app(app)

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    platforms.C_FORCE_ROOT = True

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
