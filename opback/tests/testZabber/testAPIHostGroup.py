# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Apr 15, 2016
#
# This is autotest for HostGroup API of cmdb package.

import sys, json
sys.path.append('.')

from nose.tools import *
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import *


class TestHostGroupAPI():
    '''
        Unit test for API: HostGroup/HostGroupList
    '''
    # log in
    def setUp(self):
        app.testing = True

        # # sqlite3 database for test
        # app.config['DB_FILE'] = 'test.db'
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        #                 os.path.join(app.config['DB_FOLDER'],
        #                 app.config['DB_FILE'])

        # mysql database for test
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dbuser:dbpassword@ip:port/common'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/test'
        # app.config['SQLALCHEMY_BINDS'] = {
        #     'eater': 'mysql://root:11111111@localhost:3306/eater'
        # }

        self.tester = app.test_client(self)

        # 1. db init: import user info
        db.create_all()
        # 1.2 init privileges
        user_admin_privilege = Privilege(
            privilege_name='userAdmin',
            description='user/role/privlilege administration.')
        inventory_admin_privilege = Privilege(
            privilege_name='inventoryAdmin',
            description='cmdb/inventory administration')
        shell_exec_privilege = Privilege(
            privilege_name='shellExec',
            description='execution of shell module of walker.')
        script_exec_privilege = Privilege(
            privilege_name='scriptExec',
            description='execution of script module of walker.')
        walker_info_privilege = Privilege(
            privilege_name='walkerInfo',
            description='get the details infomation of walkers.')
        user_admin_privilege.save()
        inventory_admin_privilege.save()
        shell_exec_privilege.save()
        script_exec_privilege.save()
        walker_info_privilege.save()

        # 1.3 init roles: should be committed before user init
        role_root = Role(role_name='root', description='超级用户')
        role_operator = Role(role_name='operator', description='运维操作员')
        role_inventory_admin = Role(
            role_name='inventoryAdmin', description='资源管理员')
        role_user_admin = Role(role_name='userAdmin', description='用户管理员')

        role_root.update(
            privileges=[
                inventory_admin_privilege, user_admin_privilege,
                shell_exec_privilege, script_exec_privilege,
                walker_info_privilege])
        role_user_admin.update(privileges=[user_admin_privilege])
        role_inventory_admin.update(privileges=[inventory_admin_privilege])
        role_operator.update(
            privileges=[
                shell_exec_privilege, script_exec_privilege,
                walker_info_privilege])
        role_root.save()
        role_user_admin.save()
        role_inventory_admin.save()
        role_operator.save()

        # 1.4 init users
        user1 = User(
            username='tom',
            hashed_password=userUtils.hash_pass("tompass"),
            role_list=[role_operator])
        user2 = User(
            username='jerry',
            hashed_password=userUtils.hash_pass("jerrypass"),
            role_list=[role_inventory_admin])
        user3 = User(
            username='mike',
            hashed_password=userUtils.hash_pass("mikepass"),
            role_list=[role_user_admin])
        root_user = User(
            username=app.config['DEFAULT_ROOT_USERNAME'],
            hashed_password=userUtils.hash_pass(
                app.config['DEFAULT_ROOT_PASSWORD']),
            role_list=[role_root])
        visitor = User(
            username='visitor',
            hashed_password=userUtils.hash_pass('visitor'))

        user1.save()
        user2.save()
        user3.save()
        root_user.save()
        visitor.save()

        # 2. user login: get user token
        d = {"username": app.config['DEFAULT_ROOT_USERNAME'],
             "password": app.config['DEFAULT_ROOT_PASSWORD'],
             "granttype":"login"}
        login = self.tester.post(
            '/api/v0.0/user/token',
            content_type='application/json',
            data=json.dumps(d))
        self.token = json.loads(login.data)['token']

    # log out
    def tearDown(self):
        self.token = ''
        db.session.close()
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_hostgroup_list_api_get(self):
        """
            get whole list of existing hostgroups
        """
        # 1. no paging
        response = self.tester.get(
            '/api/v0.0/hostgroup',
            headers={'token': self.token})
        assert 'data' in response.data
        eq_(response.status_code, 200)

        # 2. paging
        # 2.1 use default per page
        d = dict(page=1)
        response = self.tester.get(
            '/api/v0.0/hostgroup',
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'data' in response.data
        assert 'totalpage' in response.data
        eq_(response.status_code, 200)
        # 2.2 use custom per page
        d = dict(page=1, pp=2)
        response = self.tester.get(
            '/api/v0.0/hostgroup',
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'data' in response.data
        assert 'totalpage' in response.data
        eq_(response.status_code, 200)


    @with_setup(setUp, tearDown)
    def test_hostgroup_api_all(self):
        """
            create, get, update, delete a hostgroup
        """
        default_hostgroup_name = 'ohshalalala'

        # 1. cerate a new hostgroup
        # 1.1 hostgroup not existing yet
        d = dict(name=default_hostgroup_name)
        response = self.tester.post(
            '/api/v0.0/hostgroup',
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'data' in response.data
        eq_(response.status_code, 201)
        data = json.loads(response.data)['data']
        assert 'groupid' in data
        groupid = data['groupid']
        # 1.2 hostgroup already existing
        d = dict(name=default_hostgroup_name)
        response = self.tester.post(
            '/api/v0.0/hostgroup',
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Group Already Existing' in error
        eq_(response.status_code, 403)
        # 1.3 parameters error
        d = dict(name='')
        response = self.tester.post(
            '/api/v0.0/hostgroup',
            headers={'token': self.token},
            content_type='application/json', 
            data=json.dumps(d))
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Parameter Illegal' in error
        eq_(response.status_code, 404)

        # 2. get the created hostgroup
        # 2.1 hostgroup found
        response = self.tester.get(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token})
        assert 'data' in response.data
        eq_(response.status_code, 200)
        data = json.loads(response.data)['data']
        assert 'name' in data
        eq_(data['name'], default_hostgroup_name)
        assert 'hosts' in data

        # 3. update the created hostgroup
        # 3.1 hostgroup found
        # 3.1.1 check update action
        d = dict(name='hellopromisegroup')
        response = self.tester.put(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'data' in response.data
        eq_(response.status_code, 201)
        data = json.loads(response.data)['data']
        assert 'groupid' in data
        # 3.1.2 check update result
        response = self.tester.get(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token})
        data = json.loads(response.data)['data']
        eq_(data['name'], d['name'])
        # 3.2 hostgroup name duplication
        response = self.tester.put(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Group Already Existing' in error
        eq_(response.status_code, 403)
        # 3.3 parameters error
        d = dict(name='')
        response = self.tester.put(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Parameter Illegal' in error
        eq_(response.status_code, 404)

        # 4. delete the created hostgroup
        # 4.1 hostgroup found
        response = self.tester.delete(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token})
        eq_(response.status_code, 204)
        # 4.2 hostgroup not found
        response = self.tester.delete(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token})
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Group Not Found' in error
        eq_(response.status_code, 404)

        # 2.2 hostgroup not found (join 2.1)
        response = self.tester.get(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token})
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Group Not Found' in error
        eq_(response.status_code, 404)

        # 3.4 hostgroup not found (join 3.3)
        d = dict(name='hellopromisegroup')
        response = self.tester.put(
            '/api/v0.0/hostgroup/%s' % groupid,
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Group Not Found' in error
        eq_(response.status_code, 404)
