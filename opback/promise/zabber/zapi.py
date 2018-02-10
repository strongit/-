# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Apr 14, 2016
#
# This is the zabbix api module for the cmdb package.
#
try:
    import simplejson as json
except ImportError:
    import json

import urllib2
from .. import app


class ZabbixAPIException(Exception):
    pass


class ZabbixAPI(object):
    """
        Zabbix API for Python
    """
    __auth = ''
    __id = 0
    _state = {}

    # create a new ZabbixAPI Object if not exists
    def __new__(cls, *args, **kw):
        if cls not in cls._state:
            cls._state[cls] = super(ZabbixAPI, cls).__new__(cls, *args, **kw)
        return cls._state[cls]

    # constructor : zabbix api's [url, username, userpassword, object list]
    def __init__(self):
        self.__url = app.config['DEFAULT_ZABBIX_URL'].rstrip('/') + \
            '/api_jsonrpc.php'
        self.__user = app.config['DEFAULT_ZABBIX_USER_NAME']
        self.__password = app.config['DEFAULT_ZABBIX_PASSWORD']
        self._zabbix_api_object_list = (
            'Action', 'Alert', 'APIInfo', 'Application', 'DCheck',
            'DHost', 'DRule', 'DService', 'Event', 'Graph', 'Graphitem',
            'History', 'Host', 'Hostgroup', 'Hostinterface', 'Image',
            'Item', 'Maintenance', 'Map', 'Mediatype', 'Proxy', 'Screen',
            'Script', 'Template', 'Trigger', 'User', 'Usergroup',
            'Usermacro', 'Usermedia')

    # create a ZabbixAPIObjectFactory Object
    # named 'Action', 'Alert', ..., as a member of self
    def __getattr__(self, name):
        if name not in self._zabbix_api_object_list:
            raise ZabbixAPIException('No such Zabbix API object: %s' % name)
        if name not in self.__dict__:
            self.__dict__[name] = ZabbixAPIObjectFactory(self, name)
        return self.__dict__[name]

    # user login for zabbix api which returns an authorization token
    # as self.__auth
    def login(self):
        user_info = {'user': self.__user,
                     'password': self.__password}
        obj = self.json_obj('user.login', user_info)
        try:
            content = self.post_request(obj)
        except urllib2.HTTPError:
            raise ZabbixAPIException("Zabbix URL Error")
        try:
            self.__auth = content['result']
        except KeyError, e:
            e = content['error']['data']
            raise ZabbixAPIException(e)

    # check user login status for zabbix
    def is_login(self):
        return self.__auth != ''

    # check user authorization for zabbix
    def __checkAuth__(self):
        if not self.is_login():
            raise ZabbixAPIException("Zabbix NOT logged in")

    # jsonify parameters for zabbix api request
    def json_obj(self, method, params):
        obj = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': self.__id}
        if method != 'user.login':
            obj['auth'] = self.__auth
        return json.dumps(obj)

    # request a zabbix api
    def post_request(self, json_obj):
        headers = {'Content-Type': 'application/json',
                   'User-Agent': 'ZabbixAPI'}
        req = urllib2.Request(self.__url, json_obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        self.__id += 1
        return content


"""
   Decorate Method
"""


# add to verify authorization
def check_auth(func):
    def ret(self, *args):
        self.__checkAuth__()
        return func(self, args)
    return ret


# add to get pure zabbix api response
def zabbix_api_object_method(func):
    def wrapper(self, method_name, params):
        try:
            content = self.post_request(self.json_obj(method_name, params))
            return content['result']
        except KeyError, e:
            e = content['error']['data']
            raise ZabbixAPIException(e)
    return wrapper


class ZabbixAPIObjectFactory(object):
    """
        Zabbix API Object API (Action, Alert, Host, Item, etc.)
    """
    # the construtor
    def __init__(self, zapi, object_name=''):
        # a ZabbixAPI Object
        self.__zapi = zapi
        # a zabbix api object name like 'Action', 'Alert', ...
        self.__object_name = object_name

    # verify user authorization for zabbix using the ZabbixAPI Object
    def __checkAuth__(self):
        self.__zapi.__checkAuth__()

    # request a zabbix api using the ZabbixAPI Object
    def post_request(self, json_obj):
        return self.__zapi.post_request(json_obj)

    # jsonify parameters for zabbix api request using the ZabbixAPI Object
    def json_obj(self, method, param):
        return self.__zapi.json_obj(method, param)

    # request a zabbix api object's inner method __object_name.method_name
    # like "host.get", "host.create", ...
    def __getattr__(self, method_name):
        def method(params):
            return self.proxy_method(
                '%s.%s' % (self.__object_name, method_name), params)
        return method

    # the request proxy method
    @zabbix_api_object_method
    @check_auth
    def proxy_method(self, method_name, params):
        pass
