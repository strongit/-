# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 6, 2016
#
# This is the task module of eater package.

from .. import app, utils
from .schedules import celery
from ..zabber.models import Host, HostGroup
from .models import execute, ITEquipment, IP, Group, ITModel, OSUser, \
    Connection, Network
import random

__DoraemonUpdateNotify = 'Doraemon Update Notify: %s.'


@celery.task(bind=True, name='host_sync')
def host_sync(self):
    """
        Update host relative infos.
        From Zabber to Eater.
    """
    try:
        # mark the beginning
        msg = __DoraemonUpdateNotify % \
            'hey guys, it\'s time to update the hosts'
        app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(0, 10)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # 1. get hostgroup
        hostgroups = HostGroup().get()
        # Model Group synchronization for eater
        group = Group()
        for hg in hostgroups:
            g = group.update(id=hg['groupid'], name=hg['name'])
            if not g:
                g = group.insert(id=hg['groupid'], name=hg['name'])
            if g:
                msg = __DoraemonUpdateNotify % ('<Group %s>' % g['id'])
                app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(prog, 30)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # 2. get host
        hosts = Host().get()
        # Model ITEquipment synchronization for eater
        it = ITEquipment()
        # add default ITModel
        model = ITModel.query.filter_by(name='bclinux7').first()
        m_id = model.id if model else None
        # add default OSUser
        user = OSUser.query.filter_by(name='python_script').all()
        for h in hosts:
            g = [group.getObject(i) for i in [y['groupid']
                 for y in [x for x in h['groups']]]]
            t = it.update(id=h['hostid'], label=h['host'],
                          name=h['name'], group=g)
            if not t:
                t = it.insert(
                    id=h['hostid'], label=h['host'], name=h['name'],
                    group=g, model_id=m_id, osuser=user)
            if t:
                msg = __DoraemonUpdateNotify % ('<ITEquipment %s>' % t['id'])
                app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(prog, 70)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # Model IP synchronization for eater
        ip = IP()
        # add default Connection
        connect = Connection.query.filter_by(method='ssh', port=22).all()
        for h in hosts:
            inf = h['interfaces']
            if inf:
                # use first ip as default
                p = ip.update(id=inf[0]['interfaceid'],
                              ip_addr=inf[0]['ip'], it_id=h['hostid'])
                if not p:
                    p = ip.insert(
                        id=inf[0]['interfaceid'], ip_addr=inf[0]['ip'],
                        it_id=h['hostid'], connect=connect)
                if p:
                    msg = __DoraemonUpdateNotify % ('<IP %s>' % p['id'])
                    app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(prog, 100)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # mark the end
        msg = __DoraemonUpdateNotify % 'Host Infos are Up-to-the-Minute'
        app.logger.info(utils.logmsg(msg))
        return {'current': 100, 'total': 100, 'message': msg}
    except Exception as e:
        # mark the errors
        app.logger.error(utils.logmsg(e))
        msg = __DoraemonUpdateNotify % \
            'Error occurs while updating Host Infos.'
        app.logger.error(utils.logmsg(msg))
        return {'current': 100, 'total': 100, 'message': msg}


@celery.task(bind=True, name='network_sync')
def network_sync(self):
    """
        Update network relative infos.
        From Remote Forward Database to Eater.
    """
    import MySQLdb
    try:
        # mark the beginning
        msg = __DoraemonUpdateNotify % \
            'hey guys, it\'s time to update the networks'
        app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(0, 10)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # 1. get infos from older-forward database
        connect = MySQLdb.connect(
            host=app.config['FORWARD_DB_HOST'],
            user=app.config['FORWARD_DB_USER'],
            passwd=app.config['FORWARD_DB_PASS'],
            db=app.config['FORWARD_DB_NAME'],
            port=app.config['FORWARD_DB_PORT'],
            connect_timeout=app.config['FORWARD_DB_TIMEOUT'])
        cursor = connect.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from deviceinfo')
        result = cursor.fetchall()
        connect.close()
        if not result:
            msg = __DoraemonUpdateNotify % (
                'Sorry but nothing available now from the remote database.')
            app.logger.warn(utils.logmsg(msg))
            return {'current': 100, 'total': 100, 'message': msg}
        # for progress bar
        prog = random.randint(prog, 30)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # 2. data synchronization for eater
        # Model Network synchronization for eater
        nk = Network()
        # Model IP synchronization for eater
        ip = IP()
        # add default Connection
        for x in result:
            p = IP.query.filter_by(ip_addr=x['ip']).first()
            if p:
                connect = Connection.query.filter_by(
                    method=x['loginMethod'], port=x['port']).all()
                if ip.update(id=p.id, connect=connect):
                    msg = __DoraemonUpdateNotify % ('<IP %s>' % p.id)
                    app.logger.info(utils.logmsg(msg))
                model = ITModel.query.filter_by(
                    name=x['deviceNumber'], vender=x['deviceType']).first()
                m_id = model.id if model else None
                n = nk.update(
                    id=p.it_id, enable_pass=x['secondPassword'], model_id=m_id)
                if not n:
                    ret = execute(
                        'insert into network (id, enable_pass)'
                        ' values ("%s", "%s");' %
                        (p.it_id, x['secondPassword']))
                    if ret:
                        n = nk.update(
                            id=p.it_id, model_id=m_id, category='Network')
                if n:
                    msg = __DoraemonUpdateNotify % ('<Network %s>' % n['id'])
                    app.logger.info(utils.logmsg(msg))
            else:
                msg = __DoraemonUpdateNotify % ('Unknown <IP=%16s>' % x['ip'])
                app.logger.warn(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(prog, 100)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # mark the end
        msg = __DoraemonUpdateNotify % 'Network Infos are Up-to-the-Minute'
        app.logger.info(utils.logmsg(msg))
        return {'current': 100, 'total': 100, 'message': msg}
    except Exception as e:
        # mark the errors
        app.logger.error(utils.logmsg(e))
        msg = __DoraemonUpdateNotify % \
            'Error occurs while updating Network Infos.'
        app.logger.error(utils.logmsg(msg))
        return {'current': 100, 'total': 100, 'message': msg}
