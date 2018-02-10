# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: July 12, 2016
#
# This is autotest for cmdb models of eater package.

import sys
sys.path.append('.')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db
from promise.eater.models import *

class TestModels():
    '''
        Unit test for models in Eater
    '''
    # use test: default_bind_key = None
    default_bind_key = '__all__'

    # establish db
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

        # database initialization
        # db.drop_all(bind=self.default_bind_key)
        # db.drop_all(bind=self.default_bind_key)
        db.create_all(bind=self.default_bind_key)

        # table initialization
        # initialize osuser
        user1 = OSUser(id='u-1', name='elk', password='111111', privilege='0')
        user2 = OSUser(
            id='u-2', name='zabbix', password='111111', privilege='0')
        user3 = OSUser(id='u-3', name='joch', password='111111', privilege='1')
        db.session.add_all([user1, user2, user3])
        # initialize os
        os1 = OperatingSystem(
            user = [user1, user3], id='os-1', name='Linux',
            version='CentOS7.1')
        os2 = OperatingSystem(
            user=[user2, user3], id='os-2', name='Windows', version='Win10')
        db.session.add_all([os1, os2])
        # # initialize user2os
        # os1.user = [user1, user3]
        # os2.user.append(user2)
        # os2.user.append(user3)
        # initialize interface
        if1 = Interface(id='if-1', name='eth0')
        if2 = Interface(id='if-2', name='eth1')
        if3 = Interface(id='if-3', name='eth2')
        db.session.add_all([if1, if2, if3])
        # initialize computer specification
        cs1 = ComputerSpecification(
            id='cs-1', cpu_fre='1330Hz', cpu_num=4, memory='32G', disk='200G')
        cs2 = ComputerSpecification(
            id='cs-2', cpu_fre='1670Hz', cpu_num=8, memory='32G', disk='200G')
        cs3 = ComputerSpecification(
            id='cs-3', cpu_fre='3330Hz', cpu_num=32, memory='256G',
            disk='600G')
        db.session.add_all([cs1, cs2,cs3])
        # initialize group
        gp1 = Group(id='gp-1', name='ansible')
        gp2 = Group(id='gp-2', name='zabbix')
        gp3 = Group(id='gp-3', name='elk')
        db.session.add_all([gp1, gp2, gp3])
        # initialize pm
        pm1 = PhysicalMachine(
            inf=[if1, if2, if3], osuser = [user1, user3], id='pm-1',
            iqn_id='iqn-1', group=[gp1], spec_id='cs-2', label='NFJD-PM-1',
            name='host-pm-1', setup_time='20160701', os_id='os-1')
        pm2 = PhysicalMachine(
            inf=[if1, if2, if3], osuser = [user2], id='pm-2', iqn_id='iqn-2',
            group=[gp2, gp3], spec_id='cs-2', label='NFJD-PM-2',
            name='host-pm-2', setup_time='20160701', os_id='os-1')
        pm3 = PhysicalMachine(
            inf=[if1, if2, if3], id='pm-3', iqn_id='iqn-3', group=[gp3],
            spec_id='cs-3', label='NFJD-PM-3', name='host-pm-3',
            setup_time='20160701', os_id='os-2')
        db.session.add_all([pm1, pm2, pm3])
        # initialize vm
        vm1 = VirtualMachine(
            inf=[if1, if2], osuser = [user1], id='vm-1', pm_id='pm-1',
            vm_pid='6189', iqn_id='iqn-4', group=[gp1], spec_id='cs-2',
            label='NFJD-VM-1', name='host-vm-1', setup_time='20160701',
            os_id='os-1')
        vm2 = VirtualMachine(
            inf=[if1, if2], id='vm-2', pm_id='pm-2', vm_pid='6005',
            iqn_id='iqn-5', group=[gp1], spec_id='cs-2', label='NFJD-VM-2',
            name='host-vm-2', setup_time='20160701', os_id='os-2')
        vm3 = VirtualMachine(
            inf=[if1, if2], osuser = [user1, user2], id='vm-3', pm_id='pm-2',
            vm_pid='6009', iqn_id='iqn-6', group=[gp2, gp3], spec_id='cs-2',
            label='NFJD-VM-3', name='host-vm-3', setup_time='20160701',
            os_id='os-2')
        vm4 = VirtualMachine(
            inf=[if1, if2], id='vm-4', pm_id='pm-3', vm_pid='61899',
            iqn_id='iqn-7', spec_id='cs-1', label='NFJD-VM-4',
            name='host-vm-4', setup_time='20160701', os_id='os-1')
        db.session.add_all([vm1, vm2, vm3, vm4])
        # # initialize osuser2it
        # pm1.osuser = [user1, user3]
        # pm2.osuser = [user2]
        # vm1.osuser = [user1]
        # vm3.osuser = [user1, user2]
        # initialize vlan
        vlan1 = Vlan(
            id='vlan-1', beginning_ip='172.16.220.0',
            ending_ip='172.16.220.255')
        vlan2 = Vlan(
            id='vlan-2', beginning_ip='172.16.221.0',
            ending_ip='172.16.221.255', domain='prd',
            vlan_category='business')
        vlan3 = Vlan(
            id='vlan-3', beginning_ip='172.16.222.0',
            ending_ip='172.16.222.255', domain='dmz')
        db.session.add_all([vlan1, vlan2, vlan3])
        # initialize ip
        ip1 = IP(
            id='ip-1', ip_addr='172.16.220.1', ip_mask='255.255.255.0',
            if_id='if-1', it_id='pm-1', ip_category='pm', vlan_id='vlan-1')
        ip2 = IP(
            id='ip-2', ip_addr='172.16.220.2', ip_mask='255.255.255.0',
            if_id='if-1', it_id='pm-2', ip_category='pm', vlan_id='vlan-1')
        ip3 = IP(
            id='ip-3', ip_addr='172.16.220.3', ip_mask='255.255.255.0',
            if_id='if-1', it_id='pm-3', ip_category='pm', vlan_id='vlan-1')
        ip4 = IP(
            id='ip-4', ip_addr='172.16.221.7', ip_mask='255.255.255.0',
            if_id='if-2', it_id='pm-3', ip_category='pm', vlan_id='vlan-2')
        ip5 = IP(
            id='ip-5', ip_addr='172.16.222.4', ip_mask='255.255.255.0',
            if_id='if-1', it_id='vm-1', ip_category='vm', vlan_id='vlan-3')
        ip6 = IP(
            id='ip-6', ip_addr='172.16.222.5', ip_mask='255.255.255.0',
            if_id='if-1', it_id='vm-2', ip_category='vm', vlan_id='vlan-3')
        ip7 = IP(
            id='ip-7', ip_addr='172.16.222.6', ip_mask='255.255.255.0',
            if_id='if-1', it_id='vm-3', ip_category='vm', vlan_id='vlan-3')
        ip8 = IP(
            id='ip-8', ip_addr='172.16.222.7', ip_mask='255.255.255.0',
            if_id='if-1', it_id='vm-4', ip_category='vm', vlan_id='vlan-3')
        ip9 = IP(
            id='ip-9', ip_addr='172.16.222.254', ip_mask='255.255.255.0',
            if_id='if-1', it_id='vm-1', ip_category='vip', vlan_id='vlan-3')
        ip10 = IP(
            id='ip-10', ip_addr='172.16.222.253', ip_mask='255.255.255.0',
            if_id='if-1', it_id='pm-2', ip_category='vip', vlan_id='vlan-3')
        db.session.add_all([ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9, ip10])
        # initialize rack
        rack1 = Rack(
            id='rack-1', label='CMCC-RACK-1', it_id='pm-1', room_id='305')
        rack2 = Rack(
            id='rack-2', label='CMCC-RACK-2', it_id='pm-2', room_id='305')
        rack3 = Rack(
            id='rack-3', label='CMCC-RACK-3', it_id='pm-3', room_id='304')
        rack4 = Rack(
            id='rack-4', label='CMCC-RACK-4', it_id='pm-3', room_id='304')
        db.session.add_all([rack1, rack2, rack3, rack4])
        # do committing
        db.session.commit()

    # drop db
    def tearDown(self):
        db.session.close()
        db.drop_all(bind=self.default_bind_key)

    # super model test
    @with_setup(setUp, tearDown)
    def test_super_model(self):
        '''
        test super model for eater
        '''
        # vm0 = VirtualMachine.query.filter_by(iqn_id='iqn-4').first()
        # vm = VirtualMachine().get(iqn_id='iqn-4')
        # eq_(hasattr(VirtualMachine, '__table__'), True)
        # eq_(hasattr(Doraemon, '__table__'), False)
        # # eq_(MyModel.__bases__, True)
        # eq_(VirtualMachine.__bases__[0].__name__, 'Computer')
        # eq_(vm0.bases()[0], 'Computer')
        # eq_(VirtualMachine.__mapper__.relationships.__dict__['_data']['osuser'].strategy_class, None)
        # eq_(VirtualMachine.__mapper__.relationships.__dict__['_data'], None)
        # eq_([k for k, w in VirtualMachine.__mapper__.relationships.__dict__['_data'].items()
        #     if VirtualMachine.__name__ in str(w)], None)
        # eq_([str(w) for k, w in VirtualMachine.__mapper__.relationships.__dict__['_data'].items()], None)
        # eq_([str(w) for k, w in VirtualMachine.__mapper__.columns.__dict__['_data'].items()], None)
        # eq_([k for k, w in VirtualMachine.__mapper__.columns.__dict__['_data'].items()
        #     if VirtualMachine.__tablename__ in str(w)], None)
        # # eq_((super(VirtualMachine, vm0)).__dict__, object)
        # # eq_(vm[0], None)
        # eq_(vm[0]['id'], 'vm-1')
        # eq_(vm[0]['pm'][0]['id'], 'pm-1')
        # vm_list = VirtualMachine().get()
        # eq_(len(vm_list), 4)
        # assert vm[0] in vm_list
        # g = Group().get(id='gp-1')
        # eq_(g, None)
        # g = Group.query.filter_by(id='gp-1').first()
        # eq_(g.to_dict(), None)
        vm = VirtualMachine.query.filter_by(id='vm-1').first()
        # eq_(vm.to_dict(), None)
        it = ITEquipment.query.filter_by(id=vm.id).first()
        eq_(vm.label, it.label)
        # eq_(VirtualMachine.__mapper__.columns.__dict__['_data'], None)
        # eq_(it.to_dict(), None)
        # eq_(it.category, None)
        # eq_(vm.category, None)
        # eq_(vm.bases(), None)
        # eq_(VirtualMachine.__subclasses__(), [])
        # eq_(ITEquipment.__subclasses__(), None)
        # eq_(it, None)
        # eq_(vm.columns()['id'].nullable, it1.columns()['label'].nullable)
        # eq_(vm.relationships(), None)
        # eq_(vm.relationships()['osuser'].secondary, None)
        eq_(vm.relationships()['ip'].secondary, None)
        eq_(VirtualMachine.__mapper__.columns.__dict__['_data']['id'].nullable, False)
        # eq_(vm.columns()['id'].table, None)
        # eq_(VirtualMachine.__mapper__.columns.__dict__['_data']['id'].default, None)
        # eq_(ITEquipment.__mapper__.columns.__dict__['_data']['id'].default, False)
        eq_(vm.columns()['setup_time'].nullable, True)
        new_pm = PhysicalMachine()
        gp = Group.query.filter_by(id='gp-2').first()
        # eq_(gp.to_dict(), None)
        inf = Interface.query.filter_by(id='if-1').first()
        pm_init = new_pm.insert(
            inf=[inf], iqn_id='iqn-init', group=[gp], spec_id='cs-3',
            label='NFJD-PM-INIT', name='host-pm-init', setup_time='20160725', os_id='os-2')
        # eq_(pm_init, None)
        it_init = ITEquipment().get(id=pm_init['id'])
        eq_(pm_init['label'], it_init[0]['label'])
        it_test = ITEquipment().insert(id='it-test', label='NFJD-IT-TEST', name='host-it-test', group=[gp], os_id='os-1')
        # eq_(it_test, None)
        it_list = ITEquipment().get()
        # eq_(it_list, None)
        # eq_(pm_init, None)
        # gp_test = Group().get(id='gp-2')
        # eq_(gp_test, None)

    # model relationships test
    @with_setup(setUp, tearDown)
    def test_model_relationships(self):
        '''
        test relationships for eater
        '''
        # 1. os and osuser
        os = OperatingSystem.query.filter_by(id='os-1').first()
        user = OSUser.query.filter_by(id='u-1').first()
        assert user in os.user
        assert os in user.os
        # 2. osuser and it_equipment
        # 2.1 osuser and vm
        vm = VirtualMachine.query.filter_by(id='vm-1').first()
        it1 = ITEquipment.query.filter_by(id=vm.id).first()
        assert user in vm.osuser
        assert it1 in user.it
        # 2.2 osuser and pm
        pm = PhysicalMachine.query.filter_by(id='pm-1').first()
        it2 = ITEquipment.query.filter_by(id=pm.id).first()
        assert user in pm.osuser
        assert it2 in user.it
        # 3. pm and vm
        assert vm in pm.vm
        eq_(vm.pm_id, pm.id)
        eq_(vm.pm, pm)
        # 4. ip and it_equipment
        # 4.1 ip and pm
        ip1 = IP.query.filter_by(id='ip-9').first()
        assert ip1 in vm.ip
        eq_(ip1.it_id, vm.id)
        eq_(it1, ip1.it)
        # 4.2 ip and vm
        ip2 = IP.query.filter_by(id='ip-1').first()
        assert ip2 in pm.ip
        eq_(ip2.it_id, pm.id)
        eq_(it2, ip2.it)
        # 5. ip and interface
        inf = Interface.query.filter_by(id='if-1').first()
        assert ip1 in inf.ip
        eq_(ip1.inf, inf)
        assert ip2 in inf.ip
        eq_(ip2.inf, inf)
        # 6. computer_specification and computer
        # 6.1 computer_specification and vm
        cs = ComputerSpecification.query.filter_by(id='cs-2').first()
        eq_(vm.spec, cs)
        pc1 = Computer.query.filter_by(id=vm.id).first()
        assert pc1 in cs.computer
        # 6.2 computer_specification and pm
        pc2 = Computer.query.filter_by(id=pm.id).first()
        eq_(pm.spec, cs)
        assert pc2 in cs.computer
        # 7. it_equipment and rack
        # 7.1 pm and rack
        rack = Rack.query.filter_by(id='rack-1').first()
        assert rack in pm.rack
        eq_(it2, rack.it)
        # 8. it_equipment and interface
        # 8.1 pm and interface
        assert inf in pm.inf
        assert it2 in inf.it
        # 8.2 vm and interface
        assert inf in vm.inf
        assert it1 in inf.it
        # 9. ip and vlan
        vlan = Vlan.query.filter_by(id='vlan-1').first()
        assert ip2 in vlan.ip
        eq_(ip2.vlan_id, vlan.id)

    # computer specification model test
    @with_setup(setUp, tearDown)
    def test_computer_specification(self):
        '''
        test computer specification model for eater
        '''
        # 0. common test
        # 0.0 print test
        cs0 = ComputerSpecification(id='cs-cs', cpu_fre='1330Hz', cpu_num=8, memory='64G', disk='1T')
        eq_(cs0.__repr__(), "<ComputerSpecification %r>" % cs0.id)
        db.session.add(cs0)
        db.session.commit()
        # 0.1 check cols test
        cols, relations, isColComplete, isRelComplete = \
            cs0.checkColumnsAndRelations(
                id='cs-p', cpu_num=8, __table__='lalal', computer=None)
        eq_(cols,  {'cpu_num': 8, 'id': 'cs-p'})
        eq_(relations, {})
        # 1. insert a ComputerSpecification
        # 1.1 totally new specification
        cs1 = ComputerSpecification().insert(
            cpu_fre='1330Hz', cpu_num=4, memory='64G', disk='300G')
        eq_(cs1['cpu_num'], 4)
        eq_(cs1['computer'], [])
        # 1.2 existing specification
        cs2 = ComputerSpecification().insert(
            cpu_fre='1330Hz', cpu_num=4, memory='32G', disk='200G')
        eq_(cs2, None)
        # 2. query a ComputerSpecification
        # 2.1 by id or other factor
        cs3 = ComputerSpecification().get(id=cs1['id'])
        eq_(cs3[0]['disk'], '300G')
        # 2.2 all
        cs_list = ComputerSpecification().get()
        eq_(len(cs_list), 5)
        assert cs0,cs1 in cs_list
        # 3. update a ComputerSpecification
        # 3.1 non duplicative: update successfully
        cs4 = ComputerSpecification().update(id=cs1['id'], cpu_num=8)
        eq_(cs4['cpu_num'], 8)
        cs5 = ComputerSpecification().get(id=cs1['id'])
        eq_(cs5[0]['cpu_num'], 8)
        # 3.2 duplicative: update failed
        cs6 = ComputerSpecification().update(id=cs0.id, disk='300G')
        eq_(cs6, None)
        # 4. delete a ComputerSpecification
        # 4.1 specification exists
        flag = ComputerSpecification().delete(cs1['id'])
        eq_(flag, True)
        flag = ComputerSpecification().delete(cs0.id)
        eq_(flag, True)
        # 4.2 no such specification
        flag = ComputerSpecification().delete('boomshakalaka')
        eq_(flag, False)
        cs_list = ComputerSpecification().get()
        eq_(len(cs_list), 3)
        eq_(cs_list[0]['id'], 'cs-1')
        eq_(cs_list[1]['id'], 'cs-2')
        eq_(cs_list[2]['id'], 'cs-3')

    # virtual machine model test
    @with_setup(setUp, tearDown)
    def test_virtual_machine(self):
        '''
        test virtual machine model for eater
        '''
        # 0. common test
        # 0.0 print test
        vm0 = VirtualMachine(
            pm_id='pm-3', vm_pid='6007', iqn_id='iqn-10', spec_id='cs-2',
            label='NFJD-VM-5', name='host-vm-5', setup_time='20160725', os_id='os-2')
        eq_(vm0.__repr__(), "<VirtualMachine %r>" % vm0.id)
        db.session.add(vm0)
        db.session.commit()
        eq_(vm0.spec_id, 'cs-2')
        # 0.1 check cols test
        cols, relations, isColComplete, isRelComplete = \
            vm0.checkColumnsAndRelations(
                id='vm-vm', pm_id='pm-pm', __table__='hello', osuser=None, ip=None)
        eq_(cols,  {'id': 'vm-vm', 'pm_id': 'pm-pm'})
        eq_(relations, {'osuser': None})
        # 1. insert a VirtualMachine
        new_vm = VirtualMachine()
        # 1.1 a totally new VirtualMachine
        vm1 = new_vm.insert(
            pm_id='pm-2', vm_pid='77877', iqn_id='iqn-vm', spec_id='cs-3',
            label='NFJD-VM-VM', name='host-vm-vm', setup_time='20160725', os_id='os-2')
        eq_(vm1['pm'][0]['id'], 'pm-2')
        eq_(vm1['ip'], [])
        # 1.2 existing VirtualMachine       
        vm2 = new_vm.insert(
            pm_id='pm-3', vm_pid='6007', iqn_id='iqn-10', spec_id='cs-2',
            label='NFJD-VM-5', name='host-vm-5', setup_time='20160725', os_id='os-2')
        eq_(vm2, None)
        # 2. query a VirtualMachine
        # 2.1 by id or other factor
        vm3 = new_vm.get(id=vm1['id'])
        eq_(vm3[0]['vm_pid'], '77877')
        # 2.2 all
        vm_list = new_vm.get()
        # eq_(vm_list, None)
        eq_(len(vm_list), 6)
        assert vm0,vm1 in vm_list
        # 3. update a ComputerSpecification
        # 3.1 non duplicative: update successfully
        user1 = OSUser.query.filter_by(id='u-1').first()
        user2 = OSUser.query.filter_by(id='u-3').first()
        user3 = OSUser().getObject(id='u-3')
        eq_(user3, user2)
        vm4 = new_vm.update(id=vm0.id, spec_id='cs-3', osuser=[user1, user2])
        eq_(vm4['spec'][0]['id'], 'cs-3')
        eq_(vm4['osuser'][0]['id'], 'u-1')
        vm5 = new_vm.get(id=vm0.id)
        eq_(vm5[0]['spec_id'], 'cs-3')
        # 3.2 duplicative: update failed
        vm6 = new_vm.update(id=vm1['id'], vm_pid='6007', iqn_id='iqn-5')
        eq_(vm6, None)
        # 4. delete a VirtualMachine
        # 4.1 specification exists
        flag = new_vm.delete(vm0.id)
        eq_(flag, True)
        flag = new_vm.delete(vm1['id'])
        eq_(flag, True)
        # 4.2 no such specification
        flag = new_vm.delete('shalalala')
        eq_(flag, False)
        vm_list = new_vm.get()
        eq_(len(vm_list), 4)
        eq_(vm_list[0]['id'], 'vm-1')
        eq_(vm_list[1]['id'], 'vm-2')
        eq_(vm_list[2]['id'], 'vm-3')
        eq_(vm_list[3]['id'], 'vm-4')

    # model inheritance relationship test
    @with_setup(setUp, tearDown)
    def test_inheritance_relationship(self):
        '''
        test inheritance relationship for eater
        '''
        it0 = ITEquipment(
            id='it-0001', label='NFJD-IT-0001', name='host-it-0001')
        db.session.add(it0)
        db.session.commit()
        x = ITEquipment.query.filter_by(id=it0.id).first()
        eq_(x.name, it0.name)
        eq_(x.category, 'ITEquipment')
        db.session.delete(x)
        db.session.commit()
        cp0 = Computer(
            id=it0.id, label='NFJD-COM-0001', name=it0.name,
            iqn_id='iqn-com-0001')
        db.session.add(cp0)
        db.session.commit()    
        x = ITEquipment.query.filter_by(id=it0.id).first()
        eq_(x.name, cp0.name)
        eq_(x.category, 'Computer')
        db.session.delete(cp0)
        db.session.commit()
        vm0 = VirtualMachine(
            id=it0.id, pm_id='pm-3', vm_pid='6666', iqn_id=cp0.iqn_id,
            spec_id='cs-2', label='NFJD-VM-0001', name='host-vm-0001',
            setup_time='20160725', os_id='os-2')
        db.session.add(vm0)
        db.session.commit()
        x = ITEquipment.query.filter_by(id=it0.id).first()
        eq_(x.name, vm0.name)
        eq_(x.category, 'VirtualMachine')

        it1 = ITEquipment().insert(
            id='it-0002', label='NFJD-IT-0002', name='host-it-0002') 
        x = ITEquipment.query.filter_by(id=it1['id']).first()
        eq_(x.name, it1['name'])
        eq_(x.category, 'ITEquipment')
        db.engine.execute(
            'insert into computer (id, iqn_id) values (%r, %r);' % (
                'it-0002', 'iqn-com-0002'))
        db.session.commit()
        y = Computer.query.filter_by(id=it1['id']).first()
        eq_(y.label, x.label)
