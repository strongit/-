# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# autotest for the Privilege model of user package

import sys
sys.path.append('..')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import User, Privilege, Role
from tests import utils as testUtils

class TestApiPriv():
    '''
        Unit test for model: privilege
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
    def test_user_api_get_one_privilege(self):
        """
        test get privilege info
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        privilege = Privilege.getValidPrivilege(privilege_name='shellExec')
        rv = self.app.get(
            '/api/v0.0/user/privilege?privilege_id='+privilege.privilege_id, 
            headers = {'token': token},
            follow_redirects = True)
        print rv.data
        assert '' in rv.data
        eq_(rv.status_code, 200)#

    @with_setup(setUp, tearDown)
    def test_user_api_put_privilege(self):
        """
        test privilege put
        """
        # login with correct username & password
        [token, refreshtoken] = testUtils.getUserToken(
            self.app, 'mike', 'mikepass')
        privilege=Privilege.getValidPrivilege(privilege_name='shellExec')
        dict_data = dict(description="new description")
        rv = self.app.put(
            '/api/v0.0/user/privilege?privilege_id='+privilege.privilege_id, 
            headers = {'token': token},
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        print rv.data
        assert 'updated' in rv.data
        eq_(rv.status_code, 200)#

