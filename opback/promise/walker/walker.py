# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# A walker may have one or more trails,
# means an ansible mission work on one or more hosts.
# a shell walker will establish one ansible task with shell module
# a script walker will establish  one ansible task with script module
# a playbook walker will establish  one ansible play with a playbook
#

from flask import g
from flask_restful import reqparse, Resource
from .models import Walker, Script
from . import utils as walkerUtils
from .. import utils
from ..user import auth
import thread


class WalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(WalkerAPI, self).__init__()

    """
    Establish a script mission walker, it will return the walker id.
    A walker may have several trails(target hosts).
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    def post(self):
        pass
    """
    find out all the script-mission walkers or one of them
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    def get(self):
        walker_id = self.argCheckForGet()
        if not walker_id:
            [msg, json_walkers] = self.getWalkerListOfTokenOwner()
            return {'message': msg, 'walkers': json_walkers}, 200
        else:
            [msg, walker_name, state, json_trails] = \
                self.getWalkerInfoOfTokenOwner(walker_id)
            return {
                'message': msg,
                'walker_name': walker_name,
                'state': state,
                'trails': json_trails}, 200

    """
    arguments check methods
    """
    def argCheckForPost(self):
        self.reqparse.add_argument(
            'iplist', type=list, location='json',
            required=True, help='iplist ip must be a list')
        self.reqparse.add_argument(
            'scriptid', type=str, location='json',
            required=True, help='script_id must be a string')
        self.reqparse.add_argument(
            'params', type=list, location='json',
            help='params must be a string')
        self.reqparse.add_argument(
            'osuser', type=str, location='json',
            required=True, help='osuser must be a string')
        self.reqparse.add_argument(
            'name', type=str, location='json',
            help='default walker-name: time-scriptname')
        args = self.reqparse.parse_args()
        iplist = args['iplist']
        for ip in iplist:
            if not walkerUtils.ipFormatChk(ip):
                msg = 'wrong ip address'
                raise utils.InvalidAPIUsage(msg)
        script_id = args['scriptid']
        params = args['params']
        os_user = args['osuser']
        walker_name = args['name']
        [script, json_script] = Script.getFromIdWithinUser(
            script_id, g.current_user)
        if script:
            if not walker_name:
                walker_name = str(walkerUtils.serialCurrentTime()) + \
                    '-' + str(script.script_name)
            if params:
                params = " ".join(params)
            else:
                params = None
            return [iplist, script, os_user, params, walker_name]
        else:
            msg = 'wrong script id.'
            raise utils.InvalidAPIUsage(msg)

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'walkerid', type=str,
            location='args', help='walker id must be a string')
        args = self.reqparse.parse_args()
        walker_id = args['walkerid']
        if not walker_id:
            walker_id = None
        return walker_id

    @staticmethod
    def getWalkerListOfTokenOwner():
        [walkers, json_walkers] = Walker.getFromUser(g.current_user)
        msg = 'walker list of ' + g.current_user.username
        return [msg, json_walkers]

    @staticmethod
    def getWalkerInfo(walker_id):
        walker = Walker.getFromWalkerId(walker_id)
        if walker:
            [trails, json_trails] = Walker.getTrails(walker)
            msg = 'walker info'
        else:
            msg = 'wrong walker id'
        return [msg, walker.walker_name, json_trails]

    @staticmethod
    def getWalkerInfoOfTokenOwner(walker_id):
        [walker, json_walker] = Walker.getFromWalkerIdWithinUser(
            walker_id, g.current_user)
        if walker:
            [trails, json_trails] = walker.getTrails()
            msg = 'walker info'
            return [msg, walker.walker_name, walker.state, json_trails]
        else:
            msg = 'wrong walker id'
            raise utils.InvalidAPIUsage(msg)

    @staticmethod
    def run(shell_walker_executor):
        shell_walker_executor.run()
        thread.exit()
