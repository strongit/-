# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the mgmt module of user package,
# holding user management, privilege management, and role management, etc.
#

from flask_restful import reqparse, Resource
# User Model is named Muser, to be seperated with the User API
from .models import User, Role, Privilege
from . import auth
from .. import app, utils
from . import utils as userUtils


class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(UserAPI, self).__init__()

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def get(self):
        """
        get user list or one user info
        """
        user = self.argCheckForGet()
        if user:
            msg = 'user infomation.<user:' + user.username + '>'
            user_info = user.getDictInfo()
            return {"message": msg, "user_info": user_info}, 200
        else:
            users = User.getValidUser()
            user_info_list = list()
            for user in users:
                user_info = user.getDictInfo()
                user_info_list.append(user_info)
            msg = "infomations of all users."
            return {'message': msg, 'user_list': user_info_list}, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def post(self):
        """
        add a new user
        """
        [username, password, role_list, tel, email] = self.argCheckForPost()

        # add the new user
        user = User(
            username=username,
            hashed_password=userUtils.hash_pass(password),
            role_list=role_list,
            tel=tel,
            email=email)
        user.save()
        msg = 'user created.<user:' + user.user_id + '>'
        app.logger.info(msg)
        response = {"message": msg, "user_id": user.user_id}
        return response, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def delete(self):
        """
        delete a user
        """
        user = self.argCheckForDelete()

        # delete the new user
        user.update(valid=0)
        user.save()
        msg = 'user deleted.<user:' + user.user_id + '>'
        app.logger.info(msg)
        response = {"message": msg, "user_id": user.user_id}
        return response, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def put(self):
        """
        modf a user
        """
        [target_user, username, hashed_password, role_list, tel, email] = \
            self.argCheckForPut()
        # update user
        target_user.update(
            username=username, hashed_password=hashed_password,
            role_list=role_list, tel=tel, email=email)
        target_user.save()
        msg = 'user updated.<user:' + target_user.user_id + '>'
        app.logger.info(msg)
        response = {"message": msg, "user_id": target_user.user_id}
        return response, 200

    def argCheckForPost(self):
        self.reqparse.add_argument(
            'username', type=str, location='json',
            required=True, help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            required=True, help='password must be string')
        self.reqparse.add_argument(
            'role_id_list', type=list, location='json',
            help='role id must be string list')
        self.reqparse.add_argument(
            'tel', type=str, location='json',
            help='tel must be str')
        self.reqparse.add_argument(
            'email', type=str, location='json',
            help='email must be str')

        args = self.reqparse.parse_args()
        username = args['username']
        password = args['password']
        tel = args['tel']
        email = args['email']

        role_id_list = args['role_id_list']
        if role_id_list:
            role_list = list()
            for role_id in role_id_list:
                role = Role.getValidRole(role_id=role_id)
                if not role:
                    msg = 'invalid role id:' + role_id
                    raise utils.InvalidAPIUsage(msg)
                role_list.append(role)
        else:
            role_list = None

        user = User.getValidUser(username=username)
        if user:
            msg = 'user name is in used.'
            raise utils.InvalidAPIUsage(msg)

        return [username, password, role_list, tel, email]

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args',
            help='user_id must be string.')

        args = self.reqparse.parse_args()
        user_id = args['user_id']
        if user_id:
            user = User.getValidUser(user_id=user_id)
            if user:
                return user
            else:
                msg = 'invalid user_id.'
                raise utils.InvalidAPIUsage(msg)
        else:
            return None

    def argCheckForDelete(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args',
            required=True, help='user_id must be string.')

        args = self.reqparse.parse_args()
        user_id = args['user_id']
        user = User.getValidUser(user_id=user_id)
        if user:
            return user
        else:
            msg = 'invalid user_id.'
            raise utils.InvalidAPIUsage(msg)

    def argCheckForPut(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args',
            required=True, help='user name must be string')
        self.reqparse.add_argument(
            'username', type=str, location='json',
            help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            help='password must be string')
        self.reqparse.add_argument(
            'role_id_list', type=list, location='json',
            help='role id must be string list')
        self.reqparse.add_argument(
            'tel', type=str, location='json',
            help='tel must be str')
        self.reqparse.add_argument(
            'email', type=str, location='json',
            help='email must be str')

        args = self.reqparse.parse_args()
        # required args check
        user_id = args['user_id']
        target_user = User.getValidUser(user_id=user_id)
        if not target_user:
            msg = 'invalid user_id.'
            raise utils.InvalidAPIUsage(msg)

        # other args check
        role_id_list = args['role_id_list']
        role_list = list()
        if role_id_list:
            for role_id in role_id_list:
                role = Role.getValidRole(role_id=role_id)
                if not role:
                    msg = 'invalid role id:' + role_id
                    raise utils.InvalidAPIUsage(msg)
                role_list.append(role)

        password = args['password']
        if password:
            hashed_password = userUtils.hash_pass(password)
        else:
            hashed_password = None

        tel = args['tel']
        email = args['email']

        username = args['username']
        if username:
            user = User.getValidUser(username=username)
            if user:
                if not user.user_id == user_id:
                    msg = 'user name is in used.'
                    raise utils.InvalidAPIUsage(msg)
        elif username is '':
            msg = 'user name should not be empty string.'
            raise utils.InvalidAPIUsage(msg)
        return [target_user, username, hashed_password, role_list, tel, email]


class RoleAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(RoleAPI, self).__init__()

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def get(self):
        """
        get role list or one role info
        """
        role = self.argCheckForGet()
        if role:
            msg = 'role infomation.<role:' + role.role_name + '>'
            return {
                'message': msg,
                'role_info': role.getDictInfo()}, 200
        else:
            roles = Role.getValidRole()
            role_info_list = list()
            for role in roles:
                role_info = role.getDictInfo()
                role_info_list.append(role_info)
            msg = "infomations of all roles."
            return {"message": msg, "role_list": role_info_list}, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def post(self):
        """
        add a new role
        """
        [role_name, description, privilege_list, user_list] = \
            self.argCheckForPost()

        # add the new role
        role = Role(
            role_name=role_name,
            description=description,
            privileges=privilege_list,
            users=user_list)
        role.save()
        msg = 'role created.<role:' + role.role_id + '>'
        app.logger.info(msg)
        response = {"message": msg, "role_id": role.role_id}
        return response, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def delete(self):
        """
        delete a role
        """
        role = self.argCheckForDelete()

        # delete the role
        role.update(valid=0)
        role.save()
        msg = 'role deleted.'
        app.logger.info(msg)
        response = {"message": msg, "role_id": role.role_id}
        return response, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def put(self):
        """
        modf a role
        """
        [target_role, role_name, description, privilege_list, user_list] = \
            self.argCheckForPut()

        # update user
        target_role.update(
            role_name=role_name, privileges=privilege_list, users=user_list,
            description=description)
        target_role.save()
        msg = 'role updated.<role:' + target_role.role_id + '>'
        app.logger.info(msg)
        response = {"message": msg, "role_id": target_role.role_id}
        return response, 200

    def argCheckForPost(self):
        self.reqparse.add_argument(
            'role_name', type=str, location='json',
            required=True, help='role name must be string')
        self.reqparse.add_argument(
            'description', type=unicode, location='json',
            help='description must be string')
        self.reqparse.add_argument(
            'privilege_id_list', type=list, location='json',
            help='privilege id must be string list')
        self.reqparse.add_argument(
            'user_id_list', type=list, location='json',
            help='user id must be list')

        args = self.reqparse.parse_args()
        role_name = args['role_name']
        description = args['description']
        privilege_id_list = args['privilege_id_list']
        user_id_list = args['user_id_list']

        role = Role.getValidRole(role_name=role_name)
        if role:
            raise utils.InvalidAPIUsage('role name is in used.')
        user_list = list()
        if user_id_list:
            for user_id in user_id_list:
                user = User.getValidUser(user_id=user_id)
                if not user:
                    msg = 'invalid user id:' + user_id
                    raise utils.InvalidAPIUsage(msg)
                user_list.append(user)

        privilege_list = list()
        if privilege_id_list:
            for privilege_id in privilege_id_list:
                privilege = Privilege.getValidPrivilege(
                    privilege_id=privilege_id)
                if not privilege:
                    raise utils.InvalidAPIUsage(
                        'invalid privilege id:' + privilege_id)
                privilege_list.append(privilege)
        return [role_name, description, privilege_list, user_list]

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'role_id', type=str, location='args',
            help='role_id must be string.')

        args = self.reqparse.parse_args()
        role_id = args['role_id']
        if role_id:
            role = Role.getValidRole(role_id=role_id)
            if role:
                return role
            else:
                msg = 'invalid role_id.'
                raise utils.InvalidAPIUsage(msg)
        else:
            return None

    def argCheckForDelete(self):
        self.reqparse.add_argument(
            'role_id', type=str, location='args',
            required=True, help='role_id must be string.')

        args = self.reqparse.parse_args()
        role_id = args['role_id']
        role = Role.getValidRole(role_id=role_id)
        if role:
            return role
        else:
            msg = 'invalid role_id.'
            raise utils.InvalidAPIUsage(msg)

    def argCheckForPut(self):
        role = self.argCheckForDelete()

        self.reqparse.add_argument(
            'role_name', type=str, location='json',
            required=True, help='role name must be string')
        self.reqparse.add_argument(
            'description', type=unicode, location='json',
            help='description must be string')
        self.reqparse.add_argument(
            'privilege_id_list', type=list, location='json',
            help='privilege id must be string list')
        self.reqparse.add_argument(
            'user_id_list', type=list, location='json',
            help='user id must be list')

        args = self.reqparse.parse_args()
        role_name = args['role_name']
        description = args['description']
        privilege_id_list = args['privilege_id_list']
        user_id_list = args['user_id_list']

        role_of_name = Role.getValidRole(role_name=role_name)
        if role_of_name:
            if not role.role_id == role_of_name.role_id:
                msg = 'role name is in used.'
                raise utils.InvalidAPIUsage(msg)
        user_list = list()
        if user_id_list:
            for user_id in user_id_list:
                user = User.getValidUser(user_id=user_id)
                if not user:
                    msg = 'invalid user id:' + user_id
                    raise utils.InvalidAPIUsage(msg)
                user_list.append(user)

        privilege_list = list()
        if privilege_id_list:
            for privilege_id in privilege_id_list:
                privilege = Privilege.getValidPrivilege(
                    privilege_id=privilege_id)
                if not privilege:
                    raise utils.InvalidAPIUsage(
                        'invalid privilege id:' + privilege_id)
                privilege_list.append(privilege)
        return [role, role_name, description, privilege_list, user_list]


class PrivilegeAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(PrivilegeAPI, self).__init__()

    def get(self):
        """
        get privilege list or one privilege info
        """
        privilege = self.argCheckForGet()
        if privilege:
            msg = 'privilege infomation.<privilege:' + \
                privilege.privilege_name + '>'
            return {
                'message': msg,
                'privilege_info': privilege.getDictInfo()}, 200
        else:
            privileges = Privilege.getValidPrivilege()
            privilege_info_list = list()
            for privilege in privileges:
                privilege_info_list.append(privilege.getDictInfo())
            msg = 'infomantions of all privileges.'
            return {"message": msg, "privilege_list": privilege_info_list}, 200

    def put(self):
        """
        modf a privilege
        """
        [target_privilege, description] = self.argCheckForPut()
        # update privilege description
        target_privilege.update(description)
        target_privilege.save()
        msg = 'privilege updated.<role:' + target_privilege.privilege_id + '>'
        app.logger.info(msg)
        response = {
            "message": msg,
            "privilege_id": target_privilege.privilege_id}
        return response, 200

    def post(self):
        msg = "it is not allow to create a new privilege."
        return utils.InvalidAPIUsage(msg)

    def delete(self):
        msg = "it is Not allow to delete any privileges."
        return utils.InvalidAPIUsage(msg)

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'privilege_id', type=str, location='args',
            help='privilege_id must be string.')

        args = self.reqparse.parse_args()
        privilege_id = args['privilege_id']
        if privilege_id:
            privilege = Privilege.getValidPrivilege(privilege_id=privilege_id)
            if privilege:
                return privilege
            else:
                msg = 'invalid privilege_id.'
                raise utils.InvalidAPIUsage(msg)
        else:
            return None

    def argCheckForPut(self):
        self.reqparse.add_argument(
            'privilege_id', type=str, location='args',
            required=True, help='privilege_id must be string.')
        self.reqparse.add_argument(
            'description', type=unicode, location='json',
            required=True, help='description must be string.')
        args = self.reqparse.parse_args()
        privilege_id = args['privilege_id']
        description = args['description']
        privilege = Privilege.getValidPrivilege(privilege_id=privilege_id)
        if not privilege:
            msg = 'invalid privilege_id.'
            raise utils.InvalidAPIUsage(msg)
        return [privilege, description]
