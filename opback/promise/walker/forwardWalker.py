# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
#

from flask import g
from flask_restful import reqparse, Resource
from .models import Walker, ForwardMission, Script
from . import utils as walkerUtils
from .. import app
from forward.api import Forward
from forward.utils.error import ForwardError
from .. import utils
from ..user import auth
# import threading
# import thread
from .. import dont_cache
from tempfile import NamedTemporaryFile
import os
import json
from promise.eater import interfaces as eaterIf

# threadLock = threading.Lock()


class ForwardWalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ForwardWalkerAPI, self).__init__()

    """
    Establish a forward mission walker, it will return the walker id.
    A walker may have several trails(target hosts).
    """
    @auth.PrivilegeAuth(privilegeRequired="forwardExec")
    def post(self):
        # check the arguments
        [iplist, script, os_user, params, walker_name, inventory] = \
            self.argCheckForPost()
        # setup a walker
        walker = Walker(walker_name)

        [msg, trails] = walker.establish(iplist, g.current_user)
        # setup a scriptmission and link to the walker
        forward_mission = ForwardMission(script, os_user, params, walker)
        forward_mission.save()
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

        forward_walker_executor = ForwardWalkerExecutor(
            forward_mission, inventory)
        # run the executor thread
        # script_walker_executor.start()
        forward_walker_executor.run()

        msg = 'target forward execution established!'
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
            [msg, walker_name, state, stdout, json_trails] = \
                self.getWalkerInfoOfTokenOwner(walker_id)
            return {
                'message': msg,
                'walker_name': walker_name,
                'state': state,
                'stdout': stdout,
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
        # check all IPs of the iplist
        for ip in iplist:
            if not walkerUtils.ipFormatChk(ip):
                msg = 'wrong ip address'
                raise utils.InvalidAPIUsage(msg)
        script_id = args['scriptid']
        params = args['params']
        os_user = args['osuser']

        inventory = eaterIf.toForward(iplist)
        if not inventory:
            msg = 'cant find inventory info from eater.'
            app.logger.warning(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        else:
            msg = json.dumps(inventory)
            msg = 'inventory is ' + msg
            app.logger.warning(utils.logmsg(msg))
#        inventory = list()
#        for ip in iplist:
#            target = dict(
#                ip=ip, vender='bclinux7', model='bclinux7',
#                connect='ssh', conpass='S7fYU5', actpass='',
#                remote_port=22, remote_user=os_user,)
#            inventory.append(target)

        walker_name = args['name']

        # check if the script belongs to the current user
        script = Script.getFromIdWithinUserOrPublic(
            script_id, g.current_user)

        if not script:
            msg = 'wrong script id.'
            raise utils.InvalidAPIUsage(msg)

        # check if the script is a forward script
        if not script.script_type == 2:
            msg = "wrong script type"
            raise utils.InvalidAPIUsage(msg)

        if not walker_name:
            walker_name = str(walkerUtils.serialCurrentTime()) + \
                '-' + str(script.script_name)
        if params:
            params = params
        else:
            params = None
        return [iplist, script, os_user, params, walker_name, inventory]

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
        [walkers, json_walkers] = Walker.getForwardMissionWalker(
            g.current_user)
        msg = 'walker list of ' + g.current_user.username
        return [msg, json_walkers]

    @staticmethod
    def getWalkerInfoOfTokenOwner(walker_id):
        [walker, json_walker] = Walker.getFromWalkerIdWithinUser(
            walker_id, g.current_user)
        if not walker:
            msg = 'wrong walker id'
            raise utils.InvalidAPIUsage(msg)
        forward_mission = walker.forwardmission.first()
        if not forward_mission:
            msg = 'this is not a forward mission.'
            raise utils.InvalidAPIUsage(msg)
        [trails, json_trails] = walker.getTrails()
        msg = 'walker info'
        return [msg, walker.walker_name, walker.state, forward_mission.stdout,
                json_trails]

#    @staticmethod
#    def run(shell_walker_executor):
#        shell_walker_executor.run()
#        thread.exit()
#


# class ScriptWalkerExecutor(threading.Thread):
class ForwardWalkerExecutor(Resource):
    def __init__(self, forward_mission, inventory):
        # threading.Thread.__init__(self)
        self.forward_mission = forward_mission
        self.walker = forward_mission.getWalker()
        self.script = forward_mission.getScript()
        [trails, json_trails] = forward_mission.getTrails()
        self.trails = trails
        self.owner = self.walker.getOwner()
        self.hostnames = forward_mission.getIplist()
        self.remote_user = forward_mission.osuser
        self.script_file = self.buildScriptFile()
        self.params = forward_mission.params
        self.forward = Forward(
            worker=4, script=self.script_file.name, args=self.params,
            loglevel=app.config['FORWARD_LOGLEVEL'],
            logfile=app.config['FORWARD_LOGGER_FILE'],
            no_std_log=True, out='stdout',
            inventory=inventory, timeout=app.config['FORWARD_TIMEOUT'])

    def buildScriptFile(self):
        script_text = self.script.script_text
        script_file = NamedTemporaryFile(delete=False)
        script_file.write("""%s""" % script_text.encode('utf-8'))
        script_file.close()
        return script_file

    def run(self):
        msg = 'forward walker<id:' + self.walker.walker_id + '> begin to run.'
        app.logger.info(utils.logmsg(msg))
        print self.script_file.name

        try:
            results = self.forward.run()
            # os.remove(self.script_file.name)
        except ForwardError as e:
            msg = 'forward %s' % e
            msg = msg + 'tmp file name ' + self.script_file.name
            app.logger.warning(utils.logmsg(msg))
            self.walker.state = 1
            self.walker.save()
            raise utils.InvalidAPIUsage(msg)
#        except:
#            msg = "unknown Forward Error"
#            app.logger.info(utils.logmsg(msg))#

#        # threadLock.acquire()
        # count for the state of walker: num of failures and unreachable
        walker_state = 0
        for trail in self.trails:
            host_stat_sum = dict(
                ok=0, failures=0, unreachable=0, changed=0, skipped=0)
            host_status = results['status'][trail.ip]
            for stat in host_status:
                if host_status[stat] == 'ok':
                    host_stat_sum['ok'] += 1
                elif host_status[stat] == 'faild':
                    host_stat_sum['failures'] += 1
                elif host_status[stat] == 'unreachable':
                    host_stat_sum['unreachable'] += 1
                elif host_status[stat] == 'skipped':
                    host_stat_sum['skipped'] += 1
                elif host_status[stat] == 'changed':
                    host_stat_sum['changed'] += 1
            host_result = dict(
                msg=json.dumps(results['status'][trail.ip]))

            trail.resultUpdate(host_stat_sum, host_result)
            trail.save()

            walker_state = walker_state + host_stat_sum['failures'] + \
                host_stat_sum['unreachable']
        stdout = json.dumps(results['stdout'])
        print 'stdout:' + stdout
        self.forward_mission.stdout = unicode(stdout, 'ascii').encode('utf-8')
        self.forward_mission.save()
        self.walker.state = walker_state
        self.walker.save()
        # threadLock.release()

        msg = 'walker<id:' + self.walker.walker_id + \
            '>forwardExecutor task finished.'
        app.logger.info(utils.logmsg(msg))
        # thread.exit()
