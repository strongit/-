# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 10, 2016
#
# This is the interface module of eater package.

from .. import app
from .models import Network, IP
from .utils import decrypt


def to_forward(ip_list):
    """ Inventory Args Interface for Forward """
    if ip_list and (isinstance(ip_list, list) or isinstance(ip_list, tuple)):
        option = (
            'enable_pass', 'model', 'name', 'vender', 'osuser', 'con_pass',
            'connect', 'method', 'port', 'ip', 'id')
        inventory = []
        network = Network()
        for x in ip_list:
            ip = IP.query.filter_by(ip_addr=x).first()
            id = ip.it_id if ip else None
            if id:
                y = network.get(id=id, depth=3, option=option)
                if y:
                    y = y[0]
                    d = dict(ip=x, actpass=decrypt(
                        privatekey=app.config['FORWARD_USER_PRIVATE_KEY'],
                        ciphertext=y['enable_pass']))
                    d['model'] = y['model'][0]['name'] if y['model'] else ''
                    d['vender'] = y['model'][0]['vender'] if y['model'] else ''
                    connect = None
                    for k in y['ip']:
                        if k['id'] == ip.id:
                            connect = k['connect']
                            break
                    if connect and y['osuser']:
                        for m in y['osuser']:
                            if m['name'] == app.config['FORWARD_USERNAME']:
                                for k in m['connect']:
                                    if k in connect:
                                        d['connect'] = k['method']
                                        d['remote_port'] = k['port']
                                        d['remote_user'] = m['name']
                                        d['conpass'] = decrypt(
                                            privatekey=app.config[
                                                'FORWARD_USER_PRIVATE_KEY'],
                                            ciphertext=m['con_pass'])
                                        break
                                if len(d) == 6:
                                    break
                    else:
                        d['connect'], d['remote_port'] = '', ''
                        d['remote_user'], d['conpass'] = '', ''
                    inventory.append(d)
            else:
                pass
        return inventory
