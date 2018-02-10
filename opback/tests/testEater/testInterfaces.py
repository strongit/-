# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 1, 2016
#
# This is autotest for data interface module of eater package.

import sys, json
sys.path.append('.')

from nose.tools import *
import os
from mock import patch, Mock

# from sqlite3 import dbapi2 as sqlite3

from promise import app, db
from promise.eater.models import *


class TestInterfaces():
    '''
        Unit test for interfaces in Eater
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
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/test'
        app.config['SQLALCHEMY_BINDS'] = {
            'eater': 'mysql://root@localhost:3306/test'
        }

        self.tester = app.test_client(self)

        # database initialization
        db.create_all(bind=self.default_bind_key)

        # table initialization
        # init it model
        model = ITModel()
        model.insert(name='bclinux7', vender='bclinux7', id='m-0000')
        model.insert(name='sr7750', vender='bel', id='m-0001')
        model.insert(name='asa', vender='Cisco', id='m-0002')
        model.insert(name='asr1006', vender='Cisco', id='m-0003')
        model.insert(name='c2960', vender='Cisco', id='m-0004')
        model.insert(name='c4510', vender='Cisco', id='m-0005')
        model.insert(name='c6509', vender='Cisco', id='m-0006')
        model.insert(name='n5548', vender='Cisco', id='m-0007')
        model.insert(name='n5596', vender='Cisco', id='m-0008')
        model.insert(name='n7010', vender='Cisco', id='m-0009')
        model.insert(name='n7018', vender='Cisco', id='m-0010')
        model.insert(name='n7710', vender='cisco', id='m-0011')
        model.insert(name='n7718', vender='cisco', id='m-0012')
        model.insert(name='fw1000', vender='depp', id='m-0013')
        model.insert(name='m6000', vender='depp', id='m-0014')
        model.insert(name='f510000', vender='f5', id='m-0015')
        model.insert(name='s5800', vender='fenghuo', id='m-0016')
        model.insert(name='fg3040', vender='Fortinet', id='m-0017')
        model.insert(name='fg3950', vender='Fortinet', id='m-0018')
        model.insert(name='e8000e', vender='huawei', id='m-0019')
        model.insert(name='s9303', vender='Huawei', id='m-0020')
        model.insert(name='s9312', vender='huawei', id='m-0021')
        model.insert(name='mx960', vender='Juniper', id='m-0022')
        model.insert(name='s3300', vender='Maipu', id='m-0023')
        model.insert(name='usg1000', vender='Qimingxingchen', id='m-0024')
        model.insert(name='r3048g', vender='raisecom', id='m-0025')
        model.insert(name='af6020', vender='sinfor', id='m-0026')
        model.insert(name='m6000', vender='zte', id='m-0027')
        # init connection
        connect = Connection()
        connect.insert(method='ssh', port=22, id='conn-0001')
        connect.insert(method='telnet', port=23, id='conn-0002')
        # init os user
        osuser = OSUser()
        connect1 = Connection.query.filter_by(id='conn-0001').first()
        connect2 = Connection.query.filter_by(id='conn-0002').first()
        osuser.insert(
            id='u-0001', name='python_script',
            con_pass='50526d5765504b52ad9234f8c6723e5352d966203cd701401a006955abf8'
                     '92e6fa5d88e4a740fc95c4b33dad17518c825dafb65c9ad891ed90d1634f'
                     '532b55b1249f821a2e8480b22aa25350673cdd75b15d9cf3bf156d79168e'
                     '552ffa3a362f9bf6af5b1af1a79c22cd3d8f9b8e42806ea95227613b5f5c'
                     '7b298375a4563199',
            connect=[connect1, connect2])
        osuser.insert(
            id='u-0002', name='python_script',
            con_pass='4a6f9a31a1033319f3bf3852c8eef2ce62c607c5d40b50670234a2ea72ca'
                     'af77668f34a4f32c422be4f107071c370cde9c9b872134414674fe8f457c'
                     'a2489fd55b5e2b637d0536ba5dc42815b55ed4a83eb1603b0af7edc8f5cc'
                     '4549f58344e724cb602dadbc39d1183cd50a16aa56da0ac4aaba1638e2d1'
                     '80c053212e33a680',
            connect=[connect1])
        osuser.insert(
            id='u-0003', name='admin',
            con_pass='50526d5765504b52ad9234f8c6723e5352d966203cd701401a006955abf8'
                     '92e6fa5d88e4a740fc95c4b33dad17518c825dafb65c9ad891ed90d1634f'
                     '532b55b1249f821a2e8480b22aa25350673cdd75b15d9cf3bf156d79168e'
                     '552ffa3a362f9bf6af5b1af1a79c22cd3d8f9b8e42806ea95227613b5f5c'
                     '7b298375a4563199',
            connect=[connect1])
        osuser.insert(
            id='u-0004', name='wangluozu',
            con_pass='5269742d141b86c0856012d2ba344c736a54ec85df77f93a0d433e9827fb'
                     '259f0355dec6ab5a09698b2cdfcdf84acf0b8cbcef4ea9b8da6c9699f2ed'
                     '748d90af987000878b1c1581301af2c1e9d638432f46c3ac5f8e65dd640a'
                     '63d32699cf16d8f4b20932f5cf2b68d39a1c33276c88f2d579137e8f593a'
                     '28f194eaa7f1d407',
            connect=[connect1])
        # init network
        net = Network()
        user1 = OSUser.query.filter_by(id='u-0001').first()
        user2 = OSUser.query.filter_by(id='u-0003').first()
        net.insert(
            id='n-00001', name='njrs-n-1',
            enable_pass='5269742d141b86c0856012d2ba344c736a54ec85df77f93a0d433e9827fb'
                        '259f0355dec6ab5a09698b2cdfcdf84acf0b8cbcef4ea9b8da6c9699f2ed'
                        '748d90af987000878b1c1581301af2c1e9d638432f46c3ac5f8e65dd640a'
                        '63d328889997d8f4b20932f5cf2b68d39a1c33276c88f2d579137e8f593a'
                        '28f194eaa7f1d407',
            model_id='m-0009',
            osuser=[user1])
        net.insert(
            id='n-00002', name='njrs-n-2',
            enable_pass='5269742d141b86c0856012d2ba344c736a54ec85df77f93a0d433e9827fb'
                        '259f0355dec6ab5a09698b2cdfcdf84acf0b8cbcef4ea9b8da6c9699f2ed'
                        '748d90af987000878b1c1581301af2c1e9d638432f46c3ac5f8e65dd640a'
                        '63d32699cf16d8f4b20932f5cf2b68d39a1c33276c88f2d579137e8f593a'
                        '28f194eaa7556011',
            model_id='m-0009',
            osuser=[user1, user2])
        # init ip
        ip = IP()
        ip.insert(
            id='p-000001', ip_addr='127.0.0.1', it_id='n-00001',
            connect=[connect1])
        ip.insert(
            id='p-000002', ip_addr='127.0.0.2', it_id='n-00001',
            connect=[connect1, connect2])
        ip.insert(
            id='p-000003', ip_addr='127.0.0.3', it_id='n-00002',
            connect=[connect1, connect2])

    # drop db
    def tearDown(self):
        db.session.close()
        db.drop_all(bind=self.default_bind_key)

    @with_setup(setUp, tearDown)
    def test_interface_to_forward(self):
        """
            to forward
        """
        ip_list = ['127.0.0.1', '127.0.0.2', '127.0.0.3']
        result = None
        passwords = Mock(return_value='111111')
        # eq_(passwords.return_value, '111111')
        with patch('promise.eater.interfaces.decrypt', passwords):
            from promise.eater.interfaces import to_forward
            result = to_forward(ip_list)
        # eq_(result, None)
        eq_(result[0]['model'], 'n7010')
        eq_(result[0]['actpass'], '111111')
