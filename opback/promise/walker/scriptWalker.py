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
from .models import Walker, ScriptMission, Script
from . import utils as walkerUtils
from .. import app
from ..ansiAdapter.ansiAdapter import ScriptExecAdapter
from .. import utils
from ..user import auth
# import threading
# import thread
from .. import dont_cache

# threadLock = threading.Lock()


class ScriptWalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ScriptWalkerAPI, self).__init__()

    """
    Establish a script mission walker, it will return the walker id.
    A walker may have several trails(target hosts).
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    def post(self):
        # check the arguments
        [iplist, script, os_user, params, walker_name] = self.argCheckForPost()
        # setup a walker
        walker = Walker(walker_name)

        [msg, trails] = walker.establish(iplist, g.current_user)
        # setup a scriptmission and link to the walker
        script_mission = ScriptMission(script, os_user, params, walker)
        script_mission.save()
        walker.state = -1
        walker.save()
#        # setup a shell mission walker executor thread#

#        try:
#            script_walker_executor = ScriptWalkerExecutor(script_mission)
#            # run the executor thread
#            script_walker_executor.start()#

#            msg = 'target script execution established!'
#            return {'message': msg, 'walker_id': walker.walker_id}, 200#

#        except:
#            msg = 'faild to establish mission.'
#            walker.state = -4
#            walker.save()
#            return {'message': msg, 'walker_id': walker.walker_id}, 200
        if os_user == 'root':
            private_key_file = app.config['ROOT_SSH_KEY_FILE']
        elif os_user == 'admin':
            private_key_file = app.config['ADMIN_SSH_KEY_FILE']
        else:
            msg = 'wrong os user.'
            raise utils.InvalidAPIUsage(msg)

        script_walker_executor = ScriptWalkerExecutor(
            script_mission=script_mission,
            private_key_file=private_key_file)
        # run the executor thread
        # script_walker_executor.start()
        script_walker_executor.run()

        msg = 'target script execution established!'
        return {'message': msg, 'walker_id': walker.walker_id}, 200

    """
    find out all the script-mission walkers or one of them
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
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
            'scriptid', type=str, location='json',
            required=True, help='script_id must be a string')
        self.reqparse.add_argument(
            'params', type=unicode, location='json',
            help='params must be a string')
        self.reqparse.add_argument(
            'osuser', type=str, location='json',
            required=True, help='osuser must be a string')
        self.reqparse.add_argument(
            'name', type=str, location='json',
            help='default walker-name: time-scriptname')

        args = self.reqparse.parse_args()
        iplist = args['iplist']
        # cheak all IPs of the iplist
        for ip in iplist:
            if not walkerUtils.ipFormatChk(ip):
                msg = 'wrong ip address'
                raise utils.InvalidAPIUsage(msg)
        script_id = args['scriptid']
        params = args['params']
        os_user = args['osuser']
        walker_name = args['name']

        # check if the script belongs to the current user
        script = Script.getFromIdWithinUserOrPublic(
            script_id, g.current_user)
        if not script:
            msg = 'wrong script id.'
            raise utils.InvalidAPIUsage(msg)
        elif not script.script_type == 1:
            msg = "wrong script type"
            raise utils.InvalidAPIUsage(msg)
        elif not walker_name:
            walker_name = str(walkerUtils.serialCurrentTime()) + \
                '-' + str(script.script_name)
        elif params:
            params = " ".join(params)
            params = params.encode('utf-8')
        else:
            params = None
        return [iplist, script, os_user, params, walker_name]

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
        [walkers, json_walkers] = Walker.getScriptMissionWalker(g.current_user)
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

#    @staticmethod
#    def run(shell_walker_executor):
#        shell_walker_executor.run()
#        thread.exit()
#


# class ScriptWalkerExecutor(threading.Thread):
class ScriptWalkerExecutor(Resource):
    def __init__(self, script_mission, private_key_file='~/.ssh/id_rsa',
                 become_pass=None):
        # threading.Thread.__init__(self)
        self.script_mission = script_mission
        self.walker = script_mission.getWalker()
        self.script = script_mission.getScript()
        [trails, json_trails] = script_mission.getTrails()
        self.trails = trails
        self.owner = self.walker.getOwner()
        self.hostnames = script_mission.getIplist()
        self.remote_user = script_mission.osuser
        run_data = {
            'walker_id': self.walker.walker_id,
            'user_id': self.owner.user_id
        }
        self.script_exec_adpater = ScriptExecAdapter(
            self.hostnames,
            self.remote_user,
            private_key_file,
            run_data,
            become_pass,
            self.script.script_text,
            script_mission.params)

    def run(self):
        msg = 'walker<id:' + self.walker.walker_id + '> begin to run.'
        app.logger.info(utils.logmsg(msg))

        [state, stats_sum, results] = self.script_exec_adpater.run()
        # threadLock.acquire()
        for trail in self.trails:
            host_result = results[trail.ip]
            host_stat_sum = stats_sum[trail.ip]
            trail.resultUpdate(host_stat_sum, host_result)
            trail.save()
        self.walker.state = state
        self.walker.save()
        # threadLock.release()

        msg = 'walker<id:' + self.walker.walker_id + \
            '>scriptExecutor task finished.'
        app.logger.info(utils.logmsg(msg))
        # thread.exit()
