# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# autotest for the Auth API of user package

import sys, json
#sys.path.append('.')
sys.path.append('..')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import *
from tests import utils as testUtils
#from promise.user import *

class TestApiToken():
    '''
        Unit test for api: UserLigin
    '''
    # establish db
    def setUp(self):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            'mysql://root@localhost:3306/test'
        self.tester = app.test_client(self)
        db.create_all()
        
        testUtils.importUserData()
        print 'Data imported'

        self.app = app.test_client()

    # drop db
    def tearDown(self):
        db.drop_all()

    # test to insertting data
    @with_setup(setUp, tearDown)
    def test_user_Login(self):
        """
        test user login
        """
        # login with wrong username & password
        dict_data = dict(
                username = 'tom', password = 'tompass1',
                granttype = 'login')
        rv = self.app.post(
                '/api/v0.0/user/token',
                data=json.dumps(dict_data),
                content_type = 'application/json',
                follow_redirects = True)

        assert 'wrong username & password' in rv.data
        assert 'token' not in rv.data
        eq_(rv.status_code, 400)

        # login with correct username & password
        dict_data = dict(
                username = 'tom', password = 'tompass',
                granttype = 'login')
        rv = self.app.post(
                '/api/v0.0/user/token',
                data=json.dumps(dict_data),
                content_type = 'application/json',
                follow_redirects = True)

        assert 'logged in' in rv.data
        assert 'token' in rv.data
        eq_(rv.status_code, 200)


    @with_setup(setUp, tearDown)
    def test_user_tokenAuth(self):
        """
        auth test using token
        """
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'tom', 'tompass')
        rv = self.app.get(
            '/api/v0.0/user/token', 
            headers={'token': token},
            follow_redirects = True)
        assert 'logged in' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_tokenRefresh(self):
        """
        token refresh test using refreshToken
        """
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'tom', 'tompass')
        dict_data = dict(
                refreshtoken = refreshtoken,
                granttype = 'refreshtoken')
        rv = self.app.post(
                '/api/v0.0/user/token',
                data=json.dumps(dict_data),
                content_type = 'application/json',
                follow_redirects = True)
        print rv.data
        assert 'token refreshed' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_methodPrivelege_has_privilege(self):
        """
        test legal privilege to access one method
        """
        # 1. test root user(has privilege to access)
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app,
            app.config['DEFAULT_ROOT_USERNAME'],
            app.config['DEFAULT_ROOT_PASSWORD'])
        # use the token to get user list
        rv = self.app.get(
            '/api/v0.0/user/user', 
            headers = {'token': token},
            follow_redirects = True)
        assert 'user_list' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_methodPrivelege_donthas_privilege(self):
        """
        test ilegal privilege to access one method
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app,
            'tom',
            'tompass')
        # use the token to get user list
        rv = self.app.get(
            '/api/v0.0/user/user', 
            headers = {'token': token},
            follow_redirects = True)
        assert 'Privilege not Allowed.' in rv.data
        eq_(rv.status_code, 400)#

    @with_setup(setUp, tearDown)
    def test_user_methodPrivelege_token_tempered(self):
        """
        test tempered token to access one method
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'tom', 'tompass')
        # get the token and change it tobe a wrong token
        token = token + 'addsth.'
        rv = self.app.get(
            '/api/v0.0/user/token', 
            headers = {'token': token},
            follow_redirects = True)
        assert 'token tampered' in rv.data
        eq_(rv.status_code, 400)#

