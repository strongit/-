#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 8, 2016
#
# This is autotest for service module of eater package.

import sys, json
sys.path.append('.')

from nose.tools import *
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import *
from promise.eater.models import *
from promise.eater.tasks import host_sync


class TestServices():
    '''
        Unit test for services in Eater
    '''
    # use test: default_bind_key = None
    default_bind_key = '__all__'

    # log in
    def setUp(self):
        app.testing = True

        # sqlite3 database for test
        # app.config['DB_FILE'] = 'test.db'
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        #                 os.path.join(app.config['DB_FOLDER'],
        #                 app.config['DB_FILE'])

        # mysql database for test
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dbuser:dbpassword@ip:port/common'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/test'
        app.config['SQLALCHEMY_BINDS'] = {
            'eater': 'mysql://root@localhost:3306/test'
        }

        self.tester = app.test_client(self)

        # 1. db init: import user info
        db.create_all(bind=self.default_bind_key)

        # 1.1 cmdb initialization
        # initialize osuser
        user1 = OSUser(id='u-1', name='elk', password='111111', privilege='0')
        user2 = OSUser(id='u-2', name='zabbix', password='111111', privilege='0')
        user3 = OSUser(id='u-3', name='joch', password='111111', privilege='1')
        db.session.add_all([user1, user2, user3])
        # initialize os
        os1 = OperatingSystem(user = [user1, user3], id='os-1', name='Linux', version='CentOS7.1')
        os2 = OperatingSystem(user=[user2, user3], id='os-2', name='Windows', version='Win10')
        db.session.add_all([os1, os2])
        # initialize interface
        if1 = Interface(id='if-1', name='eth0')
        if2 = Interface(id='if-2', name='eth1')
        if3 = Interface(id='if-3', name='eth2')
        db.session.add_all([if1, if2, if3])
        # initialize computer specification
        cs1 = ComputerSpecification(id='cs-1', cpu_fre='1330Hz', cpu_num=4, memory='32G', disk='200G')
        cs2 = ComputerSpecification(id='cs-2', cpu_fre='1670Hz', cpu_num=8, memory='32G', disk='200G')
        cs3 = ComputerSpecification(id='cs-3', cpu_fre='3330Hz', cpu_num=32, memory='256G', disk='600G')
        db.session.add_all([cs1, cs2,cs3])
        # initialize group
        gp1 = Group(id='gp-1', name='ansible')
        gp2 = Group(id='gp-2', name='zabbix')
        gp3 = Group(id='gp-3', name='elk')
        db.session.add_all([gp1, gp2, gp3])
        # initialize pm
        pm1 = PhysicalMachine(inf=[if1, if2, if3], osuser = [user1, user3], id='pm-1', iqn_id='iqn-1', group=[gp1], spec_id='cs-2', label='NFJD-PM-1', name='host-pm-1', setup_time='20160701', os_id='os-1')
        pm2 = PhysicalMachine(inf=[if1, if2, if3], osuser = [user2], id='pm-2', iqn_id='iqn-2', group=[gp2, gp3], spec_id='cs-2', label='NFJD-PM-2', name='host-pm-2', setup_time='20160701', os_id='os-1')
        pm3 = PhysicalMachine(inf=[if1, if2, if3], id='pm-3', iqn_id='iqn-3', group=[gp3], spec_id='cs-3', label='NFJD-PM-3', name='host-pm-3', setup_time='20160701', os_id='os-2')
        db.session.add_all([pm1, pm2, pm3])
        # initialize vm
        vm1 = VirtualMachine(inf=[if1, if2], osuser = [user1], id='vm-1', pm_id='pm-1', vm_pid='6189', iqn_id='iqn-4', group=[gp1], spec_id='cs-2', label='NFJD-VM-1', name='host-vm-1', setup_time='20160701', os_id='os-1')
        vm2 = VirtualMachine(inf=[if1, if2], id='vm-2', pm_id='pm-2', vm_pid='6005', iqn_id='iqn-5', group=[gp1], spec_id='cs-2', label='NFJD-VM-2', name='host-vm-2', setup_time='20160701', os_id='os-2')
        vm3 = VirtualMachine(inf=[if1, if2], osuser = [user1, user2], id='vm-3', pm_id='pm-2', vm_pid='6009', iqn_id='iqn-6', group=[gp2, gp3], spec_id='cs-2', label='NFJD-VM-3', name='host-vm-3', setup_time='20160701', os_id='os-2')
        vm4 = VirtualMachine(inf=[if1, if2], id='vm-4', pm_id='pm-3', vm_pid='61899', iqn_id='iqn-7', spec_id='cs-1', label='NFJD-VM-4', name='host-vm-4', setup_time='20160701', os_id='os-1')
        db.session.add_all([vm1, vm2, vm3, vm4])
        # initialize vlan
        vlan1 = Vlan(id='vlan-1', beginning_ip='172.16.220.0', ending_ip='172.16.220.255')
        vlan2 = Vlan(id='vlan-2', beginning_ip='172.16.221.0', ending_ip='172.16.221.255', domain='prd', vlan_category='business')
        vlan3 = Vlan(id='vlan-3', beginning_ip='172.16.222.0', ending_ip='172.16.222.255', domain='dmz')
        db.session.add_all([vlan1, vlan2, vlan3])
        # initialize ip
        ip1 = IP(id='ip-1', ip_addr='172.16.220.1', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-1', ip_category='pm', vlan_id='vlan-1')
        ip2 = IP(id='ip-2', ip_addr='172.16.220.2', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-2', ip_category='pm', vlan_id='vlan-1')
        ip3 = IP(id='ip-3', ip_addr='172.16.220.3', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-3', ip_category='pm', vlan_id='vlan-1')
        ip4 = IP(id='ip-4', ip_addr='172.16.221.7', ip_mask='255.255.255.0', if_id='if-2', it_id='pm-3', ip_category='pm', vlan_id='vlan-2')
        ip5 = IP(id='ip-5', ip_addr='172.16.222.4', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-1', ip_category='vm', vlan_id='vlan-3')
        ip6 = IP(id='ip-6', ip_addr='172.16.222.5', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-2', ip_category='vm', vlan_id='vlan-3')
        ip7 = IP(id='ip-7', ip_addr='172.16.222.6', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-3', ip_category='vm', vlan_id='vlan-3')
        ip8 = IP(id='ip-8', ip_addr='172.16.222.7', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-4', ip_category='vm', vlan_id='vlan-3')
        ip9 = IP(id='ip-9', ip_addr='172.16.222.254', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-1', ip_category='vip', vlan_id='vlan-3')
        ip10 = IP(id='ip-10', ip_addr='172.16.222.253', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-2', ip_category='vip', vlan_id='vlan-3')
        db.session.add_all([ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9, ip10])
        # initialize rack
        rack1 = Rack(id='rack-1', label='CMCC-RACK-1', it_id='pm-1', room_id='305')
        rack2 = Rack(id='rack-2', label='CMCC-RACK-2', it_id='pm-2', room_id='305')
        rack3 = Rack(id='rack-3', label='CMCC-RACK-3', it_id='pm-3', room_id='304')
        rack4 = Rack(id='rack-4', label='CMCC-RACK-4', it_id='pm-3', room_id='304')
        db.session.add_all([rack1, rack2, rack3, rack4])
        db.session.commit()

        # # 1.1 init eater from zabber
        # host_sync()

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
        db.drop_all(bind=self.default_bind_key)

    @with_setup(setUp, tearDown)
    def test_hostgroup_list_api_get(self):
        """
            get hostgroup list from eater
        """
        # 1. no paging
        # 1.1 no extend
        # 1.1.1 without option
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            headers={'token': self.token})
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['totalpage'], False)
        eq_(response.status_code, 200)
        assert 'it' not in ret['data'][0]
        assert 'category' in ret['data'][0]
        assert 'name' in ret['data'][0]
        # 1.1.2 with option
        d = dict(opt='it%%name%%id')
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['totalpage'], False)
        eq_(response.status_code, 200)
        assert 'it' not in ret['data'][0]
        assert 'category' not in ret['data'][0]
        assert 'name' in ret['data'][0]
        # 1.2 extend
        # 1.2.1 without option
        d = dict(extend=True)
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['totalpage'], False)
        eq_(response.status_code, 200)
        assert 'it' in ret['data'][0]
        assert 'category' in ret['data'][0]
        assert 'name' in ret['data'][0]
        # 1.2.2 with option
        d = dict(extend=True, opt='name%%id')
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['totalpage'], False)
        eq_(response.status_code, 200)
        assert 'it' not in ret['data'][0]
        assert 'category' not in ret['data'][0]
        assert 'name' in ret['data'][0]

        # 2. paging
        # 2.1 use default per page
        d = dict(page=1)
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['totalpage'], 1)
        eq_(response.status_code, 200)
        # 2.2 use custom per page
        d = dict(page=1, pp=2)
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['totalpage'], 2)
        eq_(response.status_code, 200)

        # 3. get specific hosts
        # 3.1 no paging
        g = Group.query.first()
        d = dict(name=g.name)
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['data'][0]['name'], g.name)
        eq_(ret['totalpage'], False)
        eq_(response.status_code, 200)
        # 3.2 paging
        d = dict(page=1, name=g.name)
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup',
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        ret = json.loads(response.data)
        eq_(ret['data'][0]['name'], g.name)
        eq_(ret['totalpage'], False)
        eq_(response.status_code, 200)


    @with_setup(setUp, tearDown)
    def test_hostgroup_api(self):
        """
            get a hostgroup from eater
        """
        g = Group.query.order_by(Group.id).all()
        # 1. hostgroup found
        # 1.1 no extend
        # 1.1.1 without option
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup/%s' % g[0].id,
            headers={'token': self.token})
        assert 'data' in response.data
        eq_(response.status_code, 200)
        data = json.loads(response.data)['data']
        assert 'name' in data
        eq_(data['name'], g[0].name)
        assert 'category' in data
        assert 'it' in data
        assert 'group' not in data['it'][0]
        # 1.1.2 with option
        d = dict(opt='name%%id')
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup/%s' % g[0].id,
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        eq_(response.status_code, 200)
        data = json.loads(response.data)['data']
        assert 'name' in data
        eq_(data['name'], g[0].name)
        assert 'category' not in data
        assert 'it' not in data
        # 1.2 extend
        d = dict(extend=True)
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup/%s' % g[0].id,
            content_type='application/json',
            headers={'token': self.token},
            data=json.dumps(d))
        assert 'data' in response.data
        eq_(response.status_code, 200)
        data = json.loads(response.data)['data']
        assert 'name' in data
        eq_(data['name'], g[0].name)
        assert 'it' in data
        assert 'group' in data['it'][0]

        # 2. hostgroup not found
        response = self.tester.get(
            '/api/v0.0/eater/hostgroup/nothing',
            headers={'token': self.token})
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Object Not Found' in error
        eq_(response.status_code, 404)
