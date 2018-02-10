# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 1, 2016
#
# This is autotest for task module of eater package.

import sys, json
sys.path.append('.')

from nose.tools import *
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import *
from promise.eater.tasks import *


class TestTasks():
    '''
        Unit test for tasks in Eater
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
        db.create_all(bind=self.default_bind_key)

    # drop db
    def tearDown(self):
        db.session.close()
        db.drop_all(bind=self.default_bind_key)

    @with_setup(setUp, tearDown)
    def test_host_refresh(self):
        """
            host synchronization for eater
        """
        # insert
        eq_(host_sync()['message'],
            'Doraemon Update Notify: Host Infos are Up-to-the-Minute.')
        # update
        eq_(host_sync()['message'],
            'Doraemon Update Notify: Host Infos are Up-to-the-Minute.')

    @with_setup(setUp, tearDown)
    def test_network_refresh(self):
        """
            network synchronization for eater
        """
        import MySQLdb
        try:
            # run test if remote database exists else do nothing
            connect = MySQLdb.connect(
                host= app.config['FORWARD_DB_HOST'],
                user=app.config['FORWARD_DB_USER'],
                passwd=app.config['FORWARD_DB_PASS'],
                db=app.config['FORWARD_DB_NAME'],
                port=app.config['FORWARD_DB_PORT'],
                connect_timeout=app.config['FORWARD_DB_TIMEOUT'])
            connect.close()
            # no itequipments
            eq_(network_sync()['message'],
                'Doraemon Update Notify: Network Infos are Up-to-the-Minute.')
            # some itequipmnets
            eq_(host_sync()['message'],
                'Doraemon Update Notify: Host Infos are Up-to-the-Minute.')
            eq_(network_sync()['message'],
                'Doraemon Update Notify: Network Infos are Up-to-the-Minute.')
        except MySQLdb.Error:
            pass
