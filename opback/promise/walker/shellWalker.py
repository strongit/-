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
from .models import Walker, ShellMission
from . import utils as walkerUtils
from .. import app
from ..ansiAdapter.ansiAdapter import ShellExecAdapter
from .. import utils
from ..user import auth
import threading
import thread
from .. import dont_cache
from .. import db

threadLock = threading.Lock()


class ShellWalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ShellWalkerAPI, self).__init__()

    """
    Establish a shell mission walker, it will return the walker id.
    A walker may have several trails(target hosts).
    """
    @auth.PrivilegeAuth(privilegeRequired="shellExec")
    def post(self):
        # check the arguments
        [iplist, shell, os_user, walker_name] = self.argCheckForPost()

        # setup a walker
        walker = Walker(walker_name)

        [msg, trails] = walker.establish(iplist, g.current_user)
        # setup a shellmission and link to the walker
        shell_mission = ShellMission(shell, os_user, walker)
        shell_mission.save()
        walker.state = -1
        walker.save()
        if os_user == 'root':
            private_key_file = app.config['ROOT_SSH_KEY_FILE']
        elif os_user == 'admin':
            private_key_file = app.config['ADMIN_SSH_KEY_FILE']
        else:
            msg = 'wrong os user.'
            raise utils.InvalidAPIUsage(msg)

        # setup a shell mission walker executor
        # try:
#        shell_walker_executor = ShellWalkerExecutor(
#            shell_mission,
#            private_key_file=private_key_file)
#        shell_walker_executor.start()
#        msg = 'target shell execution established!'
#        return {'message': msg, 'walker_id': walker.walker_id}, 200
#        except:
#            msg = 'faild to establish mission.'
#            walker.state = -4
#            walker.save()
#            return {'message': msg, 'walker_id': walker.walker_id}, 200

#        shell_walker_executor = ShellWalkerExecutor(
#            shell_mission,
#            private_key_file=private_key_file)
#        shell_walker_executor.run()
        shell_walker_executor = ShellWalkerExecutorThr(
            shell_mission,
            private_key_file=private_key_file)
        shell_walker_executor.start()
        msg = 'target shell execution established!'
        return {'message': msg, 'walker_id': walker.walker_id}, 200

    """
    find out all the shell-mission walkers or one of them
    """
    @auth.PrivilegeAuth(privilegeRequired="shellExec")
    @dont_cache()
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
            'shell', type=str, location='json',
            required=True, help='shell must be a string')
        self.reqparse.add_argument(
            'osuser', type=str, location='json',
            required=True, help='osuser must be a string')
        self.reqparse.add_argument(
            'name', type=str, location='json',
            help='default walker-name: time-shell')

        args = self.reqparse.parse_args()
        iplist = args['iplist']
        for ip in iplist:
            if not walkerUtils.ipFormatChk(ip):
                msg = 'wrong ip address'
                raise utils.InvalidAPIUsage(msg)
        shell = args['shell']
        os_user = args['osuser']
        walker_name = args['name']
        if not walker_name:
            walker_name = str(walkerUtils.serialCurrentTime()) + '-' + shell

        return [iplist, shell, os_user, walker_name]

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
        [walkers, json_walkers] = Walker.getShellMissionWalker(g.current_user)
        msg = 'walker list of ' + g.current_user.username
        return [msg, json_walkers]

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
        # thread.exit()


# class ShellWalkerExecutor(threading.Thread):
class ShellWalkerExecutor(Resource):
    def __init__(self, shell_mission, private_key_file='~/.ssh/id_rsa',
                 become_pass=None):
        # threading.Thread.__init__(self)
        self.shell_mission = shell_mission
        self.walker = shell_mission.getWalker()
        [trails, json_trails] = shell_mission.getTrails()
        self.trails = trails
        self.owner = self.walker.getOwner()
        self.hostnames = shell_mission.getIplist()
        self.remote_user = shell_mission.osuser
        run_data = {
            'walker_id': self.walker.walker_id,
            'user_id': self.owner.user_id
        }
        self.shell_exec_adpater = ShellExecAdapter(
            self.hostnames,
            self.remote_user,
            private_key_file,
            run_data,
            become_pass,
            shell_mission.shell)

    def run(self):
        msg = 'walker<id:' + self.walker.walker_id + '> begin to run.'
        app.logger.info(utils.logmsg(msg))

        [state, stats_sum, results] = self.shell_exec_adpater.run()
        # threadLock.acquire()
        for trail in self.trails:
            host_result = results[trail.ip]
            host_stat_sum = stats_sum[trail.ip]
            trail.resultUpdate(host_stat_sum, host_result)
            [save_state, msg] = trail.save()
        self.walker.state = state
        self.walker.save()
        # threadLock.release()

        msg = 'walker<id:' + self.walker.walker_id + \
            '>shellExecutor task finished.'
        app.logger.info(utils.logmsg(msg))
        # thread.exit()
#        try:
#        except:
#            msg = 'walker<' + self.walker.walker_id + '> thread cannot exit.'
#            app.logger.info(utils.logmsg(msg))


class ShellWalkerExecutorThr(threading.Thread):
    def __init__(self, shell_mission, private_key_file='~/.ssh/id_rsa',
                 become_pass=None):
        threading.Thread.__init__(self)
        self.shell_mission = shell_mission
        self.walker = shell_mission.getWalker()
        [trails, json_trails] = shell_mission.getTrails()
        self.trails = trails
        self.owner = self.walker.getOwner()
        self.hostnames = shell_mission.getIplist()
        self.remote_user = shell_mission.osuser
        run_data = {
            'walker_id': self.walker.walker_id,
            'user_id': self.owner.user_id
        }
        self.shell_exec_adpater = ShellExecAdapter(
            self.hostnames,
            self.remote_user,
            private_key_file,
            run_data,
            become_pass,
            shell_mission.shell)

    def run(self):
        msg = 'walker<id:' + self.walker.walker_id + '> begin to run.'
        app.logger.info(utils.logmsg(msg))

        [state, stats_sum, results] = self.shell_exec_adpater.run()
        threadLock.acquire()
        for trail in self.trails:
            host_result = results[trail.ip]
            host_stat_sum = stats_sum[trail.ip]
            trail.resultUpdate(host_stat_sum, host_result)
            [save_state, msg] = trail.save()
        self.walker.state = state
        self.walker.save()
        threadLock.release()

        msg = 'walker<id:' + self.walker.walker_id + \
            '>shellExecutor task finished.'
        app.logger.info(utils.logmsg(msg))
        db.session.close()
        thread.exit()
