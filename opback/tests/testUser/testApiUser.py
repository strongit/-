# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is
# autotest for the Auth API of user package

import sys, json
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

class TestApiUserList():
    '''
        Unit test for api: UserList
    '''
    # establish db
    def setUp(self):
        app.testing = True
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            'mysql://root@localhost:3306/test'
        db.drop_all()
        db.create_all()
        testUtils.importUserData()
        print 'Data imported'

        self.app = app.test_client()

    # drop db
    def tearDown(self):
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_user_api_get_one_user(self):
        """
        test get one user info
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        user = User.getValidUser(username='tom')
        rv = self.app.get(
            '/api/v0.0/user/user?user_id='+user.user_id, 
            headers = {'token': token},
            follow_redirects = True)
        print rv.data
        assert 'tom' in rv.data
        eq_(rv.status_code, 200)#

    @with_setup(setUp, tearDown)
    def test_user_api_add_user(self):
        """
        test user add
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        role = Role.getValidRole(role_name='operator')
        dict_data = dict(
                username='tom1', password=userUtils.hash_pass("tompass1"),
                role_id_list=[role.role_id])
        rv = self.app.post(
            '/api/v0.0/user/user', 
            headers = {'token': token},
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        assert 'created' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_api_delete_user(self):
        """
        test user delete
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        user=User.getValidUser(username='tom')
        rv = self.app.delete(
            '/api/v0.0/user/user?user_id='+user.user_id, 
            headers = {'token': token},
            follow_redirects = True)
        assert 'delete' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_api_put_user(self):
        """
        test user put
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        user = User.getValidUser(username='tom')
        dict_data = dict(
                username='tom1', password=userUtils.hash_pass("tompass1"))
        rv = self.app.put(
            '/api/v0.0/user/user?user_id='+user.user_id, 
            headers = {'token': token},
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        print rv.data
        assert 'updated' in rv.data
        eq_(rv.status_code, 200)
