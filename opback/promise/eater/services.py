# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 10, 2016
#
# This is the service module of eater package.

from flask.ext.restful import reqparse, Resource, inputs
from ..user import auth
from .. import app, utils


"""
    Data Services
"""
from .models import ITEquipment, Group, IP


class DoraemonListAPI(Resource):
    """
        Super DataList Restful API.
        Supported By Eater.
        Methods: GET (Readonly)

        Pay attention pls:
        Attributes 'parms' and 'obj' are asked during implementation.
        'params': a list of retrievable arguments of 'obj', can be [] or ().
        'obj': an instance of one of the models belonging to Eater.
    """
    __abstract__ = True

    # constructor
    def __init__(self, obj, ignore=None, **kw):
        super(DoraemonListAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        # page
        self.parser.add_argument(
            'page', type=inputs.positive,
            help='Page must be a positive integer')
        # pp: number of items per page
        self.parser.add_argument(
            'pp', type=inputs.positive,
            help='PerPage must be a positive integer', dest='per_page')
        # if ask for more specific informations
        self.parser.add_argument(
            'extend', type=inputs.boolean,
            help='extend must be boolean')
        # options which you concern about most
        self.parser.add_argument(
            'opt', type=str,
            help='options must be splited by %%')
        # multi-type parameters
        setattr(self, 'params', [])
        type_dict = {'str_params': str, 'int_params': inputs.positive}
        for k, w in kw.items():
            if k in type_dict.keys():
                self.params.extend(w)
                for x in w:
                    self.parser.add_argument(x, type=type_dict[k])
        setattr(self, 'obj', obj)
        setattr(self, 'ignore', ignore)

    # get whole list of the object
    @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
    def get(self):
        pages, data, kw = False, [], {}
        args = self.parser.parse_args()
        for x in self.params:
            if args[x]:
                kw[x] = args[x]
        option = args['opt'].split('%%') if args['opt'] else None
        depth = 1 if args['extend'] else 0
        page = args['page']
        if kw or not page:
            data = self.obj.get(
                depth=depth, option=option, ignore=self.ignore, **kw)
        else:
            query = []
            per_page = args['per_page']
            if per_page:
                query = self.obj.get(
                    page=page, per_page=per_page, depth=depth,
                    option=option, ignore=self.ignore, **kw)
            else:
                query = self.obj.get(
                    page=page, depth=depth, option=option,
                    ignore=self.ignore, **kw)
            if query:
                data, pages = query[0], query[1]
        return {'totalpage': pages, 'data': data}, 200


class DoraemonAPI(Resource):
    """
        Super Data Restful API.
        Supported By Eater.
        for GET (Readonly)

        Pay attention pls:
        Attributes 'parms' and 'obj' are asked during implementation.
        'params': a list of attributes of 'obj', can be [] or ().
        'obj': an instance of one of the models belonging to Eater.
    """
    __abstract__ = True

    # define custom error msg
    __ParamsIllegal = 'Parameter Illegal: %s.'
    __ObjNotFound = 'Object Not Found: %s.'
    __ObjExisting = 'Object Already Existing: %s.'

    # add decorators for all
    decorators = [auth.PrivilegeAuth(
        privilegeRequired="inventoryAdmin")]

    # constructor
    def __init__(self, obj, ignore=None, **kw):
        super(DoraemonAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        # if ask for more specific informations
        self.parser.add_argument(
            'extend', type=inputs.boolean,
            help='extend must be boolean')
        # options which you concern about most
        self.parser.add_argument(
            'opt', type=str,
            help='options must be splited by %%')
        # multi-type parameters
        setattr(self, 'params', [])
        type_dict = {'str_params': str, 'int_params': inputs.positive}
        for k, w in kw.items():
            if k in type_dict.keys():
                self.params.extend(w)
                for x in w:
                    self.parser.add_argument(x, type=type_dict[k])
        setattr(self, 'obj', obj)
        setattr(self, 'ignore', ignore)

    # get a specific object
    def get(self, id):
        args = self.parser.parse_args()
        option = args['opt'].split('%%') if args['opt'] else None
        depth = 2 if args['extend'] else 1
        query = self.obj.get(
            id=id, depth=depth, option=option, ignore=self.ignore)
        if query:
            data = query[0]
            return {'data': data}, 200
        else:
            msg = self.__ObjNotFound % {'id': id}
            app.logger.error(utils.logmsg(msg))
            return {'error': msg}, 404


class HostListAPI(DoraemonListAPI):
    """
        HostList Restful API.
        Inherits from Super DataList API.
    """
    def __init__(self):
        str_params = ('category', 'label', 'name', 'os_id', 'setup_time')
        ignore = ('con_pass',)
        obj = ITEquipment()
        super(HostListAPI, self).__init__(
            str_params=str_params, obj=obj, ignore=ignore)


class HostAPI(DoraemonAPI):
    """
        Host Restful API.
        Inherits from Super Data API.
    """
    def __init__(self):
        str_params = []
        ignore = ('con_pass',)
        obj = ITEquipment()
        super(HostAPI, self).__init__(
            str_params=str_params, obj=obj, ignore=ignore)


class HostGroupListAPI(DoraemonListAPI):
    """
        HostGroupList Restful API.
        Inherits from Super DataList API.
    """
    def __init__(self):
        str_params = ('name', )
        obj = Group()
        super(HostGroupListAPI, self).__init__(
            str_params=str_params, obj=obj)


class HostGroupAPI(DoraemonAPI):
    """
        HostGroup Restful API.
        Inherits from Super Data API.
    """
    def __init__(self):
        str_params = []
        obj = Group()
        super(HostGroupAPI, self).__init__(
            str_params=str_params, obj=obj)


class IPListAPI(DoraemonListAPI):
    """
        IPList Restful API.
        Inherits from Super DataList API.
    """
    def __init__(self):
        str_params = (
            'ip_addr', 'ip_mask', 'ip_category', 'if_id', 'it_id', 'vlan_id')
        obj = IP()
        super(IPListAPI, self).__init__(str_params=str_params, obj=obj)


class IPAPI(DoraemonAPI):
    """
        IP Restful API.
        Inherits from Super Data API.
    """
    def __init__(self):
        str_params = []
        ignore = ('con_pass',)
        obj = IP()
        super(IPAPI, self).__init__(
            str_params=str_params, obj=obj, ignore=ignore)


"""
    Forward Services
"""


# class ForwardInfoAPI(DoraemonListAPI):
#     """
#         Forward Info Restful API.
#         Inherits from Super DataList API.
#     """
#     def __init__(self):
#         str_params = ['ip_addr']
#         obj = IP()
#         super(ForwardInfoAPI, self).__init__(str_params=str_params, obj=obj)

#     # get whole list of the object
#     @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
#     def get(self):
#         pages, data, kw = False, [], {}
#         args = self.parser.parse_args()
#         for x in self.params:
#             if args[x]:
#                 kw[x] = args[x]
#         depth = 2
#         page = args['page']
#         if kw or not page:
#             query = self.obj.get(depth=depth, **kw)
#         else:
#             query = []
#             per_page = args['per_page']
#             if per_page:
#                 query = self.obj.get(
#                     page=page, per_page=per_page, depth=depth, **kw)
#             else:
#                 query = self.obj.get(page=page, depth=depth, **kw)
#             if query:
#                 pages = query[1]
#                 query = query[0]
#         if query:
#             for x in query:
#                 d = {
#                     'id': x['id'], 'ip_addr': x['ip_addr'],
#                     'connect': x['connect'],
#                     'last_update_time': x['last_update_time']}
#                 if x['it']:
#                     for y in x['it']:
#                         d['model'] = y['model']
#                         d['osuser'] = y['osuser']
#                 data.append(d)
#         return {'totalpage': pages, 'data': data}, 200


"""
    Task Services
"""
from .tasks import host_sync, network_sync


class DoraemonTaskAPI(Resource):
    """
        Super Task Restful API.
        Supported By Eater.
        for POST(Execute) / GET(Check).

        Pay attention pls:
        'task_name' is asked during implementation.
        'task_name': name of the task to be executed,
                     should be a string.
    """
    # define custom error msg
    __ExeFailed = 'Execute Failed: %s.'
    __CheckFailed = 'Check Failed: %s.'

    # add decorators for all
    decorators = [auth.PrivilegeAuth(
        privilegeRequired="inventoryAdmin")]

    # constructor
    def __init__(self, task_name):
        super(DoraemonTaskAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        setattr(self, 'task_name', task_name)

    # execute a task
    def post(self):
        try:
            t = eval(self.task_name).apply_async()
            return {'id': t.task_id}, 201
        except Exception as e:
            msg = self.__ExeFailed % e
            app.logger.error(utils.logmsg(msg))
            return {'error': msg}, 500

    # check a specific task status
    def get(self, id):
        try:
            task = eval(self.task_name).AsyncResult(id)
            result = {
                'id': task.id,
                'state': task.state,
                'info': task.info
            }
            return {'result': result}, 200
        except Exception as e:
            msg = self.__CheckFailed % e
            app.logger.error(utils.logmsg(msg))
            return {'error': msg}, 500


class HostSyncAPI(DoraemonTaskAPI):
    """
        Host Synchronization Restful API.
        Inherits from Super Task API.
    """
    def __init__(self):
        super(HostSyncAPI, self).__init__(
            task_name='host_sync')


class NetworkSyncAPI(DoraemonTaskAPI):
    """
        Network Synchronization Restful API.
        Inherits from Super Task API.
    """
    def __init__(self):
        super(NetworkSyncAPI, self).__init__(
            task_name='network_sync')
