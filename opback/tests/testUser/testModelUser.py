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


class TestModelsUser():
    '''
        Unit test for model: User
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

    # drop db
    def tearDown(self):
        db.drop_all()

#    # test to insertting data
#    @with_setup(setUp, tearDown)
#    def test_role_insertinfo(self):
#        '''
#        insert user
#        '''
#        roleOperator = Role.getValidRole(role_name='operator')
#        mike = User(
#            'mike', userUtils.hash_pass("mikepass"), roleOperator)
#        mikeUserId = mike.user_id
#        mike.insertUser()
#        user = User.getValidUser(userId=mikeUserId)
#        name=user.user_name
#        name=str(name)
#        print type(name)
#        eq_(name, 'mike')
#    
#    # test to deleting data
#    @with_setup(setUp, tearDown)
#    def test_user_deleteinfo(self):
#        '''
#        delete user
#        '''
#        roleOperator = Role.getValidRole(roleName='operator')
#        mike = User('mike', userUtils.hash_pass('mikepass'),roleOperator)
#        mike.insertUser()
#        mike_test = User.getValidUser(userName='mike')
#        eq_(mike_test.user_name, 'mike')
#        mike_test.setInvalid()
#        searchUser = User.getValidUser(userId=mike_test.user_id)
#        eq_(searchUser, None)##

#    # test to updating data
#    @with_setup(setUp, tearDown)
#    def test_user_updateinfo(self):
#        '''
#        update user
#        '''
#        user = User.getValidUser(userName='tom')
#        user.hashed_password = userUtils.hash_pass('tompass1')
#        User.updateUser(user)
#        user_get = User.getValidUser(userName='tom')
#        eq_(user_get.hashed_password, userUtils.hash_pass('tompass1'))##

#    # test to get data
#    @with_setup(setUp, tearDown)
#    def test_user_getinfo(self):
#        '''
#        get user & get Relate role
#        '''
#        user = User.getValidUser(userName='tom')
#        eqTag = 0
#        roles = user.roles
#        for role in roles:
#            if role.role_name == 'operator':
#                eqTag = 1
#        eq_(eqTag, 1)#

#    # test userLogin4Token
#    @with_setup(setUp, tearDown)
#    def test_user_Login4token(self):
#        '''
#        test login for token
#        '''
#        testUser = User.getValidUser(userName='jerry')
#        [token, refreshToken, user, msg] = User.userLogin4token('jerry', 'jerrypass')
#        print msg
#        eq_(user.user_id, testUser.user_id)


