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

class TestApiRole():
    '''
        Unit test for api: role
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
    def test_user_api_get_one_role(self):
        """
        test get one role info
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        role = Role.getValidRole(role_name='operator')
        rv = self.app.get(
            '/api/v0.0/user/role?role_id='+role.role_id, 
            headers = {'token': token},
            follow_redirects = True)
        assert 'operator' in rv.data
        eq_(rv.status_code, 200)#

    @with_setup(setUp, tearDown)
    def test_user_api_add_role(self):
        """
        test role add
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        dict_data = dict(
                role_name='new role name', description="description")
        rv = self.app.post(
            '/api/v0.0/user/role', 
            headers = {'token': token},
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        print rv.data
        assert 'create' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_api_delete_role(self):
        """
        test role delete
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        role=Role.getValidRole(role_name='operator')
        rv = self.app.delete(
            '/api/v0.0/user/role?role_id='+role.role_id, 
            headers = {'token': token},
            follow_redirects = True)
        assert 'delete' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_api_put_role(self):
        """
        test role put
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        role=Role.getValidRole(role_name='operator')
        dict_data = dict(
                role_name='new role name', description="description")
        rv = self.app.put(
            '/api/v0.0/user/role?role_id='+role.role_id, 
            headers = {'token': token},
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        print rv.data
        assert 'updated' in rv.data
        eq_(rv.status_code, 200)
