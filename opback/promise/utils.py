# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the Utils module for the Global package of promise,
# holding some useful tools, and setting up the Eceptions
#
import uuid
from . import app, api
from flask import request, make_response, json


def genUuid(seq):
    """
        generate a 64Byte uuid code
        first 32Byte: hashed timestamp string,
        last 32Byte: hashed 'seq' string in its namespace
        in the user package, it is used to create 'User.user_id'
    """
    newUuid = uuid.uuid1().hex + uuid.uuid3(uuid.NAMESPACE_DNS, seq).hex
    return newUuid

"""
    logger
"""
# Init the Logging Handler
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(app.config['LOGGER_FILE'],
                              maxBytes=102400,
                              backupCount=1)
handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.DEBUG)


def logmsg(msg):
    """
        to format the log message: add remote ip and target url
        add other info if u need more
    """
    try:
        logmsg = msg + '[from ' + request.remote_addr + \
            ' to ' + request.url + ']'
    except:
        logmsg = msg
    return logmsg


"""
    Exception: 2 custom Exception classes,
    1. api calling exception, means exterior error(client exception)
    2. module calling exception, means internal error(server exception)
"""


class InvalidAPIUsage(Exception):
    """
        invalid API usage, belongs to client exception,
        use the 4xx status_code
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        # setLevel can be [debug, info, warning, error, critical]
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class InvalidModuleUsage(Exception):
    """
        invalid module calling, belongs to server exception,
        use the 5xx status_code
    """
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        # setLevel can be [debug, info, warning, error, critical]
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

"""
    establish the handler for the custom exceptions
    include formatting errormessage into json type
"""
from flask import jsonify
from . import app


# handler for the InvalidModuleUsage custom exception class
@app.errorhandler(InvalidModuleUsage)
def handle_invalid_module_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# handler for the InvalidAPIUsage custom exception class
@app.errorhandler(InvalidAPIUsage)
def handle_invalid_api_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# return a normal restful json response
@api.representation('application/json')
def responseJson(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp
