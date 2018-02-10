# -*- coding:utf-8 -*-
from app import celery, create_app


app = create_app()
app.app_context().push()
