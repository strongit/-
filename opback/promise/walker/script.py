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
from .models import Script
from .. import utils
from ..user import auth
from .. import dont_cache


class ScriptAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ScriptAPI, self).__init__()

    """
    insert a new script.
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    def post(self):
        # check the arguments
        [script_name, script_text, script_lang, is_public, script_type] = \
            self.argCheckForPost()

        # create a script object
        print script_type
        script = Script(
            script_name, script_text, g.current_user, script_lang, is_public,
            script_type)
        script.save()
        msg = 'script created.'
        return {'message': msg, 'script_id': script.script_id}, 200

    @auth.PrivilegeAuth(privilegeRequired='scriptExec')
    def put(self):
        # check the arguments
        [script_id, script_name, script_text, script_lang,
         is_public, script_type] = self.argCheckForPut()
        # modify target script object
        [script, jsonScript] = Script.getFromIdWithinUser(
            script_id, g.current_user)
        if script:
            script.update(
                script_name, script_text, script_lang, g.current_user,
                is_public, script_type)
            script.save()
            msg = 'script<id:' + script.script_id + '>uptaded'
            return {'message': msg}, 200
        else:
            msg = 'wrong script id or its not your script'
            raise utils.InvalidAPIUsage(msg)

    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    @dont_cache()
    def get(self):
        [script_id, script_type] = self.argCheckForGet()
        if not script_id:
            callableScripts = Script.getCallableScripts(
                user=g.current_user, script_type=script_type)
            json_callableScripts = list()
            for callableScript in callableScripts:
                result = dict()
                result['script_id'] = callableScript.Script.script_id
                result['script_name'] = callableScript.Script.script_name
                result['script_text'] = callableScript.Script.script_text
                result['owner_name'] = callableScript.User.username
                result['owner_id'] = callableScript.Script.owner_id
                result['time_create'] = callableScript.Script.time_create
                result['time_last_edit'] = \
                    callableScript.Script.time_last_edit
                result['is_public'] = callableScript.Script.is_public
                result['script_lang'] = callableScript.Script.script_lang
                result['script_type'] = callableScript.Script.script_type
                json_callableScripts.append(result)
            msg = 'got script list.'
            return {'message': msg, 'scripts': json_callableScripts}, 200
        else:
            callableScript = Script.getCallableScripts(
                user=g.current_user, script_id=script_id)
            if not callableScript:
                msg = 'cant find script.'
                raise utils.InvalidAPIUsage(msg)

            result = dict()
            result['script_id'] = callableScript.Script.script_id
            result['script_name'] = callableScript.Script.script_name
            result['script_text'] = callableScript.Script.script_text
            result['owner_name'] = callableScript.User.username
            result['owner_id'] = callableScript.Script.owner_id
            result['time_create'] = callableScript.Script.time_create
            result['time_last_edit'] = callableScript.Script.time_last_edit
            result['is_public'] = callableScript.Script.is_public
            result['script_lang'] = callableScript.Script.script_lang
            result['script_type'] = callableScript.Script.script_type
            msg = 'got target script.'
            return {'message': msg, 'script': result}, 200

    @auth.PrivilegeAuth(privilegeRequired='scriptExec')
    def delete(self):
        script_id = self.argCheckForDelete()
        [script, jsonScript] = Script.getFromIdWithinUser(
            script_id, g.current_user)
        if not script:
            msg = 'wrong script_id.'
            raise utils.InvalidAPIUsage(msg)
        [state, msg] = script.setInvalid()
        if state:
            return {'message': msg}, 200
        else:
            raise utils.InvalidAPIUsage(msg)

    """
    arguments check methods
    """
    def argCheckForGet(self):
        self.reqparse.add_argument(
            'script_id', type=str,
            location='args', help='script id must be a string')
        self.reqparse.add_argument(
            'script_type', type=int,
            location='args',
            help='script type must be a int,1:ansible;2:forward')
        args = self.reqparse.parse_args()
        script_id = args['script_id']
        if not script_id:
            script_id = None
        script_type = args['script_type']
        if not script_type:
            script_type = None
        return [script_id, script_type]

    def argCheckForPost(self):
        self.reqparse.add_argument(
            'script_name', type=str, location='json',
            required=True, help='iplist ip must be a list')
        self.reqparse.add_argument(
            'script_text', type=unicode, location='json',
            required=True, help='script_text must be a unicode text')
        self.reqparse.add_argument(
            'script_lang', type=str, location='json',
            required=True, help='osuser must be a string')
        self.reqparse.add_argument(
            'is_public', type=int, location='json',
            required=True, help='is_public must be 0 or 1')
        self.reqparse.add_argument(
            'script_type', type=int, location='json',
            help='script_type must be 1 for ansible or 2 for forward')
        args = self.reqparse.parse_args()
        script_name = args['script_name']
        script_text = args['script_text']
        script_lang = args['script_lang']
        is_public = args['is_public']
        script_type = args['script_type']
        if not script_type:
            script_type = 1
        return [script_name, script_text, script_lang, is_public, script_type]

    def argCheckForPut(self):
        self.reqparse.add_argument(
            'script_id', type=str, location='args',
            required=True, help='script_id must be a string')
        self.reqparse.add_argument(
            'script_name', type=str, location='json',
            required=True, help='iplist_name must be a list')
        self.reqparse.add_argument(
            'script_text', type=unicode, location='json',
            required=True, help='script_text must be a unicode text')
        self.reqparse.add_argument(
            'script_lang', type=str, location='json',
            required=True, help='script_lang must be a string')
        self.reqparse.add_argument(
            'is_public', type=int, location='json',
            required=True, help='is_public must be 0 or 1')
        self.reqparse.add_argument(
            'script_type', type=int, location='json',
            required=True, help='script_type must be 0 or 1')
        args = self.reqparse.parse_args()
        script_id = args['script_id']
        script_name = args['script_name']
        script_text = args['script_text']
        script_lang = args['script_lang']
        is_public = args['is_public']
        script_type = args['script_type']
        return [script_id, script_name, script_text, script_lang, is_public,
                script_type]

    def argCheckForDelete(self):
        self.reqparse.add_argument(
            'script_id', type=str, required=True,
            location='args', help='script id must be a string')
        args = self.reqparse.parse_args()
        script_id = args['script_id']
        return script_id

    @staticmethod
    def getScriptListOfTokenOwner():
        [scripts, json_scripts] = Script.getWithinUser(g.current_user)
        if json_scripts:
            msg = 'scripts info'
            return [msg, json_scripts]
        else:
            msg = 'no scripts exist.'
            return [msg, None]

    @staticmethod
    def getExcutableScriptsInfo():
        pass

    @staticmethod
    def getScriptInfo(script_id):
        [script, json_script] = Script.getFromIdWithinUser(
            script_id, g.current_user)
        if script:
            msg = 'walker info'
            return [msg, json_script]
        else:
            msg = 'wrong script id'
            return [msg, None]
