# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the utils of user package,
# holding some useful tools for the user package
#
from .. import app
import md5
import datetime
import re


def hash_pass(password):
    """
        Create a quick list of password.  The password is stored
        as a md5 hash that has also been salted.  You should never
        store the users password and only store the password after
        it has been hashed.
    """
    secreted_password = password + app.config['SECRET_KEY']
    salted_password = md5.new(secreted_password).hexdigest() +\
        app.config['PSW_SALT']
    return md5.new(salted_password).hexdigest()


def serialCurrentTime():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


def ipFormatChk(ip_str):
    pattern_string = r"""
       \b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b
       """
    pattern = re.compile(pattern_string, re.X)
    if re.match(pattern, ip_str):
        return True
    else:
        return False
