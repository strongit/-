# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# autotest for the Role model of user package

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

class TestModelsRole():
    '''
        Unit test for model: Role
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

#   # drop db
#    def tearDown(self):
#        db.drop_all()#

#    # test to insertting data
#    @with_setup(setUp, tearDown)
#    def test_role_insertinfo(self):
#        '''
#        insert role
#        '''
#        role = Role('root1')
#        role.save()
#        root1 = Role.getValidRole(roleName='root1')#

#        rolename = root1.role_name
#        name = str(rolename)
#        print name
#        eq_(rolename, 'root1')
#    
##    # test to deleting data
#    @with_setup(setUp)
#    def test_role_deleteinfo(self):
#        '''
#        delete role
#        '''
#        role = Role('root1')
#        role.save()
#        root1 = Role.getValidRole(roleName='root1')
#        eq_(root1.role_name, 'root1')
#        root1_test = Role.getValidRole(roleName='root1')
#        root1_test.setInvalid()
#        role = Role.getValidRole(roleId=root1_test.role_id)
#        print role
#        eq_(role, None)##

##    # test to updating data
#    @with_setup(setUp, tearDown)
#    def test_user_updateinfo(self):
#        '''
#        update role
#        '''
#        root = Role.getValidRole(roleName='root')
#        root.role_name = 'root1'
#        db.session.commit()
#        roleGet = Role.getValidRole(roleId=root.role_id)
#        eq_(roleGet.role_name, 'root1')#

##    # test to get data
#    @with_setup(setUp, tearDown)
#    def test_role_getinfo(self):
#        '''
#        get role
#        '''
#        role = Role.getValidRole(roleName='root')
#        eq_(role.role_name, 'root')
