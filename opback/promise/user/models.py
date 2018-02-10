# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the model module for the user package
# holding user, token, role and  privilege models, etc.
#
from .. import db, app
from .. import utils, ma
from sqlalchemy import sql, and_

import datetime


"""
This is a HELPER table for the role_table and user_table to set up
the many-to-many relationship between Role modole and User model.
As Flask official documentation recommanded, this helper table
should not be a model but an actual table.
"""
roles = db.Table(
    'roles',
    db.Column(
        'role_id',
        db.String(64),
        db.ForeignKey('role.role_id')),
    db.Column(
        'user_id',
        db.String(64),
        db.ForeignKey('user.user_id'))
)

"""
This is a HELPER table for the privilege_table and role_table to set up
the many-to-many relationship between Role modole and privilege model.
As Flask official documentation recommanded, this helper table
should not be a model but an actual table.
"""
privileges = db.Table(
    'privileges',
    db.Column(
        'privilege_id',
        db.String(64),
        db.ForeignKey('privilege.privilege_id')),
    db.Column(
        'role_id',
        db.String(64),
        db.ForeignKey('role.role_id'))
)


class User(db.Model):
    """
    User model
    For the sake of Operation Audit, u shouldn't delete any user.
    Instead, u can set user into 'invalid' status. so I privide the
    'setInvalid()' method to do this.
    """
    __tablename__ = 'user'
    # user_id is a 64Byte UUID depend on the timestamp, namespace and username
    user_id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    hashed_password = db.Column(db.String(128))
    valid = db.Column(db.SmallInteger)
    last_login = db.Column(db.DATETIME)
    tel = db.Column(db.String(32))
    email = db.Column(db.String(32))
    sign_up_date = db.Column(db.DATETIME)
    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('roles', lazy='select'))

    def __init__(
            self, username, hashed_password,
            role_list=None, valid=1, tel=None, email=None):
        self.user_id = utils.genUuid(username)
        self.username = username
        self.hashed_password = hashed_password
        self.valid = valid
        if tel:
            self.tel = tel
        if email:
            self.email = email
        if role_list:
            self.roles = role_list
        self.sign_up_date = datetime.datetime.now()

    def __repr__(self):
        return '<User %r>' % self.user_id

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('save user ' + self.username + ' to db.')
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    @staticmethod
    def getValidUser(username=None, user_id=None):
        if username is not None and user_id is None:
            user = User.query.filter_by(username=username, valid=1).first()
        elif username is None and user_id is not None:
            user = User.query.filter_by(user_id=user_id, valid=1).first()
        elif username and user_id:
            user = User.query.filter_by(
                user_id=user_id, username=username).first()
        else:
            user = User.query.filter_by(valid=1).all()
        return user

    def getDictInfo(self):
        priv_list = self.getPrivilegeList()
        role_list = self.getRoleList()
        user_info = {
            "username": self.username,
            "user_id": self.user_id,
            "sign_up_date": self.sign_up_date,
            "last_login": self.last_login,
            "tel": self.tel,
            "email": self.email,
            "role": role_list,
            "privilege": priv_list}
        return user_info

    def getPrivilegeList(self, valid=1):
        q = sql.select(
            [Privilege.privilege_name, Privilege.description]).where(
            and_(
                roles.c.user_id == self.user_id,
                roles.c.role_id == privileges.c.role_id,
                privileges.c.privilege_id == Privilege.privilege_id,
                Privilege.valid == valid))
        db_exec = db.session.execute(q)
        rest = db_exec.fetchall()
        db_exec.close()
        priv_list = list()
        for priv in rest:
            priv_list.append({
                'name': priv.privilege_name,
                'description': priv.description})
        return priv_list

    def getPrivilegeNameList(self, valid=1):
        q = sql.select(
            [Privilege.privilege_name]).where(
            and_(
                roles.c.user_id == self.user_id,
                roles.c.role_id == privileges.c.role_id,
                privileges.c.privilege_id == Privilege.privilege_id,
                Privilege.valid == 1))
        db_exec = db.session.execute(q)
        rest = db_exec.fetchall()
        db_exec.close()
        priv_list = list()
        for priv in rest:
            priv_list.append(priv.privilege_name)
        return priv_list

    def getRoleList(self, valid=1):
        q = sql.select([Role.role_name, Role.description]).where(
            and_(
                roles.c.user_id == self.user_id,
                roles.c.role_id == Role.role_id,
                Role.valid == valid))
        db_exec = db.session.execute(q)
        rest = db_exec.fetchall()
        db_exec.close()
        role_name_list = list()
        for role in rest:
            role_name_list.append({
                'name': role.role_name,
                'description': role.description})
        return role_name_list

    def update(
            self, username=None, hashed_password=None, last_login=None,
            tel=None, email=None, sign_up_date=None, valid=None,
            role_list=None):
        if username is not None:
            self.username = username
        if hashed_password is not None:
            self.hashed_password = hashed_password
        if last_login is not None:
            self.last_login = last_login
        if tel is not None:
            self.tel = tel
        if email is not None:
            self.email = email
        if sign_up_date is not None:
            self.sign_up_date = sign_up_date
        if valid is not None:
            self.valid = valid
        if role_list is not None:
            self.roles = role_list
        app.logger.debug(utils.logmsg(
            'user info update user:' + self.username))

    def privilege_validation(self, privilege_id):
        q = sql.select([roles.c.role_id]).where(
            and_(
                privileges.c.privilege_id == privilege_id,
                roles.c.user_id == self.user_id,
                roles.c.role_id == privileges.c.role_id))
        db_exec = db.session.execute(q)
        rest = db_exec.fetchall()
        db_exec.close()
        if rest:
            return True
        else:
            return False


class Role(db.Model):
    """
    role model
    """
    __tablename__ = 'role'
    # role_id is a 64Byte UUID depend on the timestamp, namespace and rolename
    role_id = db.Column(db.String(64), primary_key=True)
    role_name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    valid = db.Column(db.SmallInteger)
    privileges = db.relationship(
        'Privilege',
        secondary=privileges,
        backref=db.backref('privileges', lazy='select'))
    users = db.relationship(
        'User',
        secondary=roles,
        backref=db.backref('role', lazy='select'))

    def __repr__(self):
        return '<Role %r>' % self.role_id

    def __init__(
            self, role_name, description=None, users=None, privileges=None,
            valid=1):
        self.role_id = utils.genUuid(role_name)
        self.role_name = role_name
        self.description = description
        self.valid = valid
        if users is not None:
            self.users = users
        if privileges is not None:
            self.privileges = privileges

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('save role ' + self.role_name + ' to db.')
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    def update(
            self, role_name=None, valid=None, privileges=None, users=None,
            description=None):
        if role_name:
            self.role_name = role_name
        if valid is not None:
            self.valid = valid
        if privileges is not None:
            self.privileges = privileges
        if users is not None:
            self.users = users
        if description is not None:
            self.description = description
        app.logger.debug(utils.logmsg(
            'role info update role:' + self.role_name))

    @staticmethod
    def getValidRole(role_name=None, role_id=None, valid=1):
        if role_name is not None and role_id is None:
            role = Role.query.filter_by(
                role_name=role_name, valid=valid).first()
        elif role_name is None and role_id is not None:
            role = Role.query.filter_by(role_id=role_id, valid=valid).first()
        elif role_name and role_id:
            role = Role.query.filter_by(
                role_id=role_id, role_name=role_name, valid=valid).first()
        else:
            role = Role.query.filter_by(valid=valid).all()
            print "use else"
        return role

    def getPrivilegeList(self, valid=1):
        q = sql.select([Privilege]).where(
            and_(
                privileges.c.role_id == self.role_id,
                privileges.c.privilege_id == Privilege.privilege_id,
                Privilege.valid == valid))
        db_exec = db.session.execute(q)
        target_privileges = db_exec.fetchall()
        db_exec.close()
        return privileges_schema.dump(target_privileges).data

    def getUserList(self, valid=1):
        q = sql.select([User]).where(
            and_(
                roles.c.role_id == self.role_id,
                roles.c.user_id == User.user_id,
                User.valid == valid))
        db_exec = db.session.execute(q)
        target_users = db_exec.fetchall()
        db_exec.close()
        return users_schema.dump(target_users).data

    def getDictInfo(self):
        priv_list = self.getPrivilegeList()
        user_list = self.getUserList()
        role_info = {
            "role_name": self.role_name,
            "role_id": self.role_id,
            "privilege": priv_list,
            "user": user_list,
            "description": self.description}
        return role_info

    def setInvalid(self):
        self.privileges = []
        self.users = []
        self.valid = 0


class Privilege(db.Model):
    """
    privilege model
    """
    __tablename__ = 'privilege'
    # privilege_id is a 64Byte UUID depend on the timestamp, namespace and
    # privilege name
    privilege_id = db.Column(db.String(64), primary_key=True)
    privilege_name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    valid = db.Column(db.SmallInteger)
    roles = db.relationship(
        'Role',
        secondary=privileges,
        backref=db.backref('privilege', lazy='select'))

    def __repr__(self):
        return '<privilege %r>' % self.privilege_id

    def __init__(self, privilege_name, description, valid=1):
        self.privilege_id = utils.genUuid(privilege_name)
        self.privilege_name = privilege_name
        self.description = description
        self.valid = valid

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg(
                'save privilege ' + self.privilege_name + ' to db.')
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    def update(self, description=None, valid=None):
        if valid is not None:
            self.valid = valid
        if description is not None:
            self.description = description
        app.logger.debug(utils.logmsg(
            'privilege info update:' + self.privilege_name))

    @staticmethod
    def getValidPrivilege(privilege_id=None, privilege_name=None, valid=1):
        if privilege_id is not None and privilege_name is None:
            privilege = Privilege.query.filter_by(
                privilege_id=privilege_id, valid=1).first()
        elif privilege_id is None and privilege_name is not None:
            privilege = Privilege.query.filter_by(
                privilege_name=privilege_name, valid=1).first()
        elif privilege_id and privilege_name:
            privilege = Privilege.query.filter_by(
                privilege_id=privilege_id,
                privilege_name=privilege_name,
                valid=1).first()
        else:
            privilege = Privilege.query.filter_by(valid=1).all()
        return privilege

    def getDictInfo(self):
        role_list = self.getRoleList()
        user_list = self.getUserList()
        role_info = {
            "privilege_name": self.privilege_name,
            "privilege_id": self.privilege_id,
            "description": self.description,
            "role": role_list,
            "user": user_list}
        return role_info

    def getRoleList(self):
        roles = self.roles
        return roles_schema.dump(roles).data

    def getUserList(self):
        q = sql.select([User]).where(
            and_(
                privileges.c.privilege_id == self.privilege_id,
                privileges.c.role_id == roles.c.role_id,
                roles.c.user_id == User.user_id,
                User.valid == 1))
        db_exec = db.session.execute(q)
        users = db_exec.fetchall()
        db_exec.close()
        return users_schema.dump(users).data


#####################################################################
#    establish a meta data class for data print                     #
#####################################################################
class UserSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'last_login', 'tel', 'email',
            'sign_up_date']

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class RoleSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Role
        fields = ['role_id', 'role_name', 'description']

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)


class PrivilegeSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Privilege
        fields = ['privilege_id', 'privilege_name', 'description']

privilege_schema = PrivilegeSchema()
privileges_schema = PrivilegeSchema(many=True)
