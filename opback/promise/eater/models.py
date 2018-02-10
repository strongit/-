# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 6, 2016
#
# This is the model module of eater package.

from .. import db, app, utils  # , ma
from sqlalchemy.ext.declarative import declared_attr
import re
from datetime import datetime


def execute(sql):
    try:
        db.engine.execute(sql)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        msg = 'Tabel Execute Exception: %s' % e
        app.logger.error(utils.logmsg(msg))
    return False

# default database bound
# my_default_database = None
my_default_database = 'eater'


class Doraemon(db.Model):
    """
        Eater Super Model.
    """
    __abstract__ = True

    __DoraemonContraintException = 'Doraemon Contraint Exception: %s.'

    # tablename
    @declared_attr
    def __tablename__(cls):
        pattern = re.compile(r'([A-Z]+[a-z]+|^[A-Z]+[^A-Z]*$)')
        words = pattern.findall(cls.__name__)
        tname = ''
        if len(words) > 1:
            for w in words[:-1]:
                tname += '%s_' % w
        tname += words[-1]
        return tname.lower()

    # uuid
    @declared_attr
    def id(cls):
        return db.Column(
            db.String(64), primary_key=True)

    # category
    @declared_attr
    def category(cls):
        return db.Column(db.String(64))

    # last update time
    @declared_attr
    def last_update_time(cls):
        return db.Column(
            db.DateTime, onupdate=datetime.now(), default=datetime.now())

    # name list of base classes
    def bases(self):
        names = []
        for x in self.__class__.__bases__:
            names.append(x.__name__)
        return names

    # list of model columns
    def columns(self):
        return self.__class__.__mapper__.columns.__dict__['_data']

    # list of model columns: not include columns of super classes
    def own_columns(self):
        return {k: w for k, w in self.columns().items()
                if self.__tablename__ in str(w)}

    # list of model relationships
    def relationships(self):
        return self.__class__.__mapper__.relationships.__dict__['_data']

    # list of model relationships: not include relationships of super classes
    def own_relationships(self):
        return {k: w for k, w in self.relationships().items()
                if self.__class__.__name__ in str(w)}

    # constructor
    def __init__(self, **kw):
        if kw:
            cols, relations, isColComplete, isRelComplete = \
                self.checkColumnsAndRelations(**kw)
            if isColComplete:
                d = dict(cols, **relations)
                for k, w in d.items():
                    setattr(self, k, w)
                if 'id' not in d.keys():
                    setattr(self, 'id', utils.genUuid(self.__class__.__name__))
                # set category by default
                setattr(self, 'category', self.__class__.__name__)

    # for print
    def __str__(self):
        return '<%s %r>' % (self.__class__.__name__, self.id)
    __repr__ = __str__

    # output columns and relationships to dict using recursive method
    def to_dict(self, count=0, depth=1, option=None, ignore=None):
        columns = self.columns().keys()
        relationships = self.relationships().keys()
        # if you want to drop something
        # `ignore` has higher priority than `option`
        if ignore and (isinstance(ignore, list) or isinstance(ignore, tuple)):
            columns = [x for x in columns if x not in ignore]
        # see what you concern about
        if option and (isinstance(option, list) or isinstance(option, tuple)):
            columns = [x for x in columns if x in option]
            relationships = [x for x in relationships if x in option]
        # get columns
        d = {k: getattr(self, k) for k in columns}
        # recursion ends (better limit depth to be <= 3)
        # or it may risk to be maximum recursion depth exceeded
        depth = 3 if depth > 3 else depth
        if not relationships or count == depth:
            return d
        count += 1
        # get relationships
        for k in relationships:
            relation = getattr(self, k)
            if relation:
                if hasattr(relation, '__iter__'):
                    d[k] = [x.to_dict(
                        count=count, depth=depth, option=option, ignore=ignore)
                        for x in relation if hasattr(x, 'to_dict')]
                elif hasattr(relation, 'to_dict'):
                    d[k] = [relation.to_dict(
                        count=count, depth=depth, option=option,
                        ignore=ignore)]
            else:
                d[k] = []
        return d

    # # output columns and relationships to dict using schema
    # # ---- schema has been deprecated cuz proved to be a waste of time ----
    # # also when using the schema, foreign_keys are forbidden to be left NULL
    # def to_dict(self):

    #     class DoraemonSchema(ma.ModelSchema):
    #         """
    #             Model Schema.
    #         """
    #         class Meta:
    #             model = self.__class__

    #     dorae = DoraemonSchema().dump(self).data
    #     # ModelSchema ignore foreign_keys as default
    #     if 'id' not in dorae.keys():
    #         dorae['id'] = self.id
    #     return dorae

    # find out params in table columns and relationships
    def checkColumnsAndRelations(self, **kw):
        cols, relations = {}, {}
        isColComplete, isRelComplete = True, True
        columns = self.columns()
        relationships = self.relationships()
        if kw:
            # check columns
            for k, w in columns.items():
                if k in kw.keys():
                    cols[k] = kw[k]
                elif (not w.nullable) and (not w.default) and (k is not 'id'):
                    # non-nullable column which has no default value
                    # should not be left
                    isColComplete = False
            # check relationships
            for k, w in relationships.items():
                if (k in kw.keys()) and (w.secondary is not None):
                    # only many-to-many relationship
                    # can be initialized in this way
                    relations[k] = kw[k]
                elif w.secondary is not None:
                    # only many-to-many relationship
                    # should be initialized in this way
                    isRelComplete = False
        return cols, relations, isColComplete, isRelComplete

    # see if relative records exist
    # input dict{}: conditions for search
    # ouput boolean: True if exists, False if not
    def _exist(self, **kw):
        if kw:
            cols, relations, isColComplete, isRelComplete = \
                self.checkColumnsAndRelations(**kw)
            li = self.__class__.query.filter_by(
                **cols).order_by(self.__class__.id).all()
            if li:
                return li
        return None

    # insert a record
    # input dict{}:
    # whole factors (except id, which is optional) of a new record
    # output dict{}: the inserted new record
    def insert(self, depth=1, ignore=None, **kw):
        if kw:
            obj = self.__class__(**kw)
            db.session.add(obj)
            try:
                db.session.commit()
                return obj.to_dict(depth=depth, ignore=ignore)
            except Exception, e:
                db.session.rollback()
                msg = self.__DoraemonContraintException % e
                app.logger.error(utils.logmsg(msg))
        return None

    # update a record
    # input: str: id, dict{}: factors to update
    # output dict{}: the updated record
    def update(self, id, depth=1, ignore=None, **kw):
        obj = self.__class__.query.filter_by(id=id).first()
        if obj:
            cols, relations, isColComplete, isRelComplete = \
                self.checkColumnsAndRelations(**kw)
            d = dict(cols, **relations)
            for k, w in d.items():
                setattr(obj, k, w)
            # set last update time by default
            setattr(obj, 'last_update_time', datetime.now())
            try:
                db.session.commit()
                return obj.to_dict(depth=depth, ignore=ignore)
            except Exception, e:
                db.session.rollback()
                msg = self.__DoraemonContraintException % e
                app.logger.error(utils.logmsg(msg))
        return None

    # get (a) record(s)
    # input dict{}: conditions for search
    # output json list[]: record(s) s.t. conditions
    def get(self, page=None, per_page=20, depth=1, option=None,
            ignore=None, **kw):
        if not kw:
            if page:
                li = self.__class__.query.paginate(page, per_page, False)
            else:
                li = self.__class__.query.order_by(self.__class__.id).all()
        else:
            li = self._exist(**kw)
        if li:
            if not kw and page:
                return [
                    x.to_dict(depth=depth, option=option, ignore=ignore)
                    for x in li.items], li.pages
            return [x.to_dict(
                depth=depth, option=option, ignore=ignore) for x in li]
        return []

    # get an object by id
    # input str: object id for search
    # output db.Model (only used for many-to-many relationships)
    def getObject(self, id):
        li = self._exist(id=id)
        if li:
            return li[0]
        return None

    # delete a record
    # input str: id
    # output boolean: True if deleted, False if failed to delete
    def delete(self, id):
        old_rec = self.__class__.query.filter_by(id=id).first()
        if old_rec:
            db.session.delete(old_rec)
            try:
                db.session.commit()
                return True
            except Exception, e:
                db.session.rollback()
                msg = self.__DoraemonContraintException % e
                app.logger.error(utils.logmsg(msg))
        return False


"""
many-to-many relationships between IP and Connection
"""
connect2ip = db.Table(
    'connect2ip',
    db.Column('connect_id', db.String(64), db.ForeignKey('connection.id')),
    db.Column('ip_id', db.String(64), db.ForeignKey('ip.id')),
    info={'bind_key': my_default_database}
)


"""
many-to-many relationships between OSUser and Connection
"""
osuser2connect = db.Table(
    'osuser2connect',
    db.Column('connect_id', db.String(64), db.ForeignKey('connection.id')),
    db.Column('osuser_id', db.String(64), db.ForeignKey('osuser.id')),
    info={'bind_key': my_default_database}
)


"""
many-to-many relationships between OperatingSystem and OSUser
"""
user2os = db.Table(
    'user2os',
    db.Column('os_id', db.String(64), db.ForeignKey('operating_system.id')),
    db.Column('user_id', db.String(64), db.ForeignKey('osuser.id')),
    info={'bind_key': my_default_database}
)


"""
many-to-many relationships between ITEquipment and OSUser
"""
osuser2it = db.Table(
    'osuser2it',
    db.Column('it_id', db.String(64), db.ForeignKey('itequipment.id')),
    db.Column('osuser_id', db.String(64), db.ForeignKey('osuser.id')),
    info={'bind_key': my_default_database}
)


"""
many-to-many relationships between ITEquipment and Interface
"""
if2it = db.Table(
    'if2it',
    db.Column('if_id', db.String(64), db.ForeignKey('interface.id')),
    db.Column('it_id', db.String(64), db.ForeignKey('itequipment.id')),
    info={'bind_key': my_default_database}
)


"""
many-to-many relationships between Group and ITEquipment
"""
it2group = db.Table(
    'it2group',
    db.Column('it_id', db.String(64), db.ForeignKey('itequipment.id')),
    db.Column('group_id', db.String(64), db.ForeignKey('group.id')),
    info={'bind_key': my_default_database}
)


class IP(Doraemon):
    """
        IP Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint(
            'ip_addr', 'ip_mask', 'ip_category',
            'if_id', 'vlan_id', 'it_id', name='_ip_uc'),)

    # IP address
    ip_addr = db.Column(db.String(64), unique=True)
    # IP mask
    ip_mask = db.Column(db.String(64))
    # IP category (vm/pm/network/security/storage/ipmi/vip/unused)
    ip_category = db.Column(db.String(64))
    # interface which IP belongs to
    if_id = db.Column(db.String(64), db.ForeignKey('interface.id'))
    # IT equipment which IP belongs to
    it_id = db.Column(db.String(64), db.ForeignKey('itequipment.id'))
    # vlan which IP belongs to
    vlan_id = db.Column(db.String(64), db.ForeignKey('vlan.id'))
    # way to connect to IP
    connect = db.relationship(
        'Connection', secondary='connect2ip',
        enable_typechecks=False, lazy='dynamic')


class Connection(Doraemon):
    """
        Connection Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('method', 'port', name='_com_uc'),)

    # connection method name
    method = db.Column(db.String(64))
    # connection port
    port = db.Column(db.Integer)
    # IP
    ip = db.relationship(
        'IP', secondary='connect2ip',
        enable_typechecks=False, lazy='dynamic')
    # OS user
    osuser = db.relationship(
        'OSUser', secondary='osuser2connect',
        enable_typechecks=False, lazy='dynamic')


class Vlan(Doraemon):
    """
        Vlan Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint(
            'beginning_ip', 'ending_ip', 'domain',
            'vlan_category', name='_vlan_uc'),)

    # ip range start from
    beginning_ip = db.Column(db.String(64), nullable=False)
    # ip range end to
    ending_ip = db.Column(db.String(64), nullable=False)
    # domain: dmz/core/prd/mgmt
    domain = db.Column(db.String(64), default='mgmt')
    # vlan category: management/business/storage
    vlan_category = db.Column(db.String(64), default='management')
    # vlan used IP
    ip = db.relationship('IP', backref='vlan', lazy='dynamic')


class Interface(Doraemon):
    """
        Interface Model.
    """
    __bind_key__ = my_default_database

    # interface name
    name = db.Column(db.String(64), unique=True)
    # IP
    ip = db.relationship('IP', backref='inf', lazy='dynamic')
    # IT equipment
    it = db.relationship(
        'ITEquipment', secondary='if2it',
        enable_typechecks=False, lazy='dynamic')


class OperatingSystem(Doraemon):
    """
        Operating System Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('name', 'version', name='_os_uc'),)

    # OS name
    name = db.Column(db.String(64), nullable=False)
    # OS version
    version = db.Column(db.String(64), nullable=False)
    # IT equipment
    it = db.relationship(
        'ITEquipment', backref='os', lazy='dynamic')
    # OS user
    user = db.relationship(
        'OSUser', secondary='user2os', backref='os', lazy='dynamic')


class OSUser(Doraemon):
    """
        Operating System User Model.
        Set 'enable_typechecks=False' to enable subtype polymorphism.
    """
    __bind_key__ = my_default_database
    # __table_args__ = (
    #     db.UniqueConstraint(
    #         'name', 'con_pass', name='_osuser_uc', ),)

    # OS user name
    name = db.Column(db.String(64), nullable=False)
    # OS user connection password
    con_pass = db.Column(db.String(256))
    # IT equipment
    it = db.relationship(
        'ITEquipment', secondary='osuser2it',
        enable_typechecks=False, lazy='dynamic')
    # way to connect to IT equipment
    connect = db.relationship(
        'Connection', secondary='osuser2connect',
        enable_typechecks=False, lazy='dynamic')


class Rack(Doraemon):
    """
        Rack Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('label', 'it_id', name='_rack_uc'),)

    # rack label
    label = db.Column(db.String(64), unique=True)
    # room which rack belongs to
    room_id = db.Column(db.String(64), nullable=False)
    # IT equipment which is installed in the rack
    it_id = db.Column(db.String(64), db.ForeignKey('itequipment.id'))


class ITEquipment(Doraemon):
    """
        IT Equipment Model.
        Superclass of Computer, Network, Storage and Security.
        Set 'enable_typechecks=False' to enable subtype polymorphism.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint(
            'label', 'name', 'setup_time', 'os_id', 'model_id',
            name='_it_uc'),)

    # IT equipment label
    label = db.Column(db.String(64), unique=True)
    # IT equipment host name
    name = db.Column(db.String(64), unique=True)
    # IT equipment setup time
    setup_time = db.Column(db.String(64))
    # operating system
    os_id = db.Column(db.String(64), db.ForeignKey('operating_system.id'))
    # IT equipment model id
    model_id = db.Column(db.String(64), db.ForeignKey('itmodel.id'))
    # OS user
    osuser = db.relationship(
        'OSUser', secondary='osuser2it',
        enable_typechecks=False, lazy='dynamic')
    # business group
    group = db.relationship(
        'Group', secondary='it2group',
        enable_typechecks=False, lazy='dynamic')
    # interface
    inf = db.relationship(
        'Interface', secondary='if2it',
        enable_typechecks=False, lazy='dynamic')
    # IT equipment IP
    ip = db.relationship(
        'IP', enable_typechecks=False, backref='it', lazy='dynamic')
    # IT equipment location
    rack = db.relationship(
        'Rack', enable_typechecks=False, backref='it', lazy='dynamic')


class ITModel(Doraemon):
    """
        IT Model Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('name', 'vender', name='_it_mod_uc'),)

    # IT equipment model name
    name = db.Column(db.String(64))
    # IT equipment vender
    vender = db.Column(db.String(64))
    # IT equipment
    it = db.relationship(
        'ITEquipment', backref='model', lazy='dynamic')


class Computer(ITEquipment):
    """
        Computer Model.
        Child of ITEquipment.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('spec_id', 'iqn_id', name='_com_uc'),)

    # use super class ITEquipment uuid as Computer uuid
    id = db.Column(
        db.String(64), db.ForeignKey('itequipment.id'),
        primary_key=True)
    # iscsi name
    iqn_id = db.Column(db.String(64), nullable=True, unique=True)
    # computer specification
    spec_id = db.Column(
        db.String(64), db.ForeignKey('computer_specification.id'))


class ComputerSpecification(Doraemon):
    """
        Computer Specification Model.
    """
    __bind_key__ = my_default_database

    # each specification must be unique
    # which either insert() or update() is subject to
    __table_args__ = (
        db.UniqueConstraint(
            'cpu_fre', 'cpu_num', 'memory', 'disk', name='_spec_uc'),)

    # CPU main frequency
    cpu_fre = db.Column(db.String(64), nullable=False)
    # CPU number
    cpu_num = db.Column(db.Integer, nullable=False)
    # memory
    memory = db.Column(db.String(64), nullable=False)
    # hard disk size
    disk = db.Column(db.String(64), nullable=False)
    # IT equipment IP
    computer = db.relationship(
        'Computer', backref='spec', lazy='dynamic')


class PhysicalMachine(Computer):
    """
        Physical Machine Model.
        Child of Computer.
    """
    __bind_key__ = my_default_database

    # use super class Computer uuid as PysicalMachine uuid
    id = db.Column(
        db.String(64), db.ForeignKey('computer.id'),
        primary_key=True)
    # related virtual machines
    vm = db.relationship(
        'VirtualMachine',
        backref='pm',
        foreign_keys='VirtualMachine.pm_id',
        lazy='dynamic')


class VirtualMachine(Computer):
    """
        Virtual Machine Model.
        Child of Computer.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('pm_id', 'vm_pid', name='_pm_vm_uc'),)

    # use super class Computer uuid as VirtualMachine uuid
    id = db.Column(
        db.String(64), db.ForeignKey('computer.id'),
        primary_key=True)
    # related pm
    pm_id = db.Column(
        db.String(64), db.ForeignKey('physical_machine.id'))
    # vm pid
    vm_pid = db.Column(db.String(64), nullable=False)


class Network(ITEquipment):
    """
        Network Model.
        Child of ITEquipment.
    """
    __bind_key__ = my_default_database

    # use super class ITEquipment uuid as Network uuid
    id = db.Column(
        db.String(64), db.ForeignKey('itequipment.id'),
        primary_key=True)
    # Network enable password
    enable_pass = db.Column(db.String(256))


class Firewall(Network):
    """
        Firewall Model.
        Child of Network.
    """
    __bind_key__ = my_default_database

    # use super class Network uuid as Firewall uuid
    id = db.Column(
        db.String(64), db.ForeignKey('network.id'),
        primary_key=True)


class Router(Network):
    """
        Router Model.
        Child of Network.
    """
    __bind_key__ = my_default_database

    # use super class Network uuid as Router uuid
    id = db.Column(
        db.String(64), db.ForeignKey('network.id'),
        primary_key=True)


class Switch(Network):
    """
        Switch Model.
        Child of Network.
    """
    __bind_key__ = my_default_database

    # use super class Network uuid as Switch uuid
    id = db.Column(
        db.String(64), db.ForeignKey('network.id'),
        primary_key=True)


class Group(Doraemon):
    """
        Host Group Model.
    """
    __bind_key__ = my_default_database

    # group name
    name = db.Column(db.String(64), unique=True)
    # IT equipment
    it = db.relationship(
        'ITEquipment', secondary='it2group',
        enable_typechecks=False, lazy='dynamic')
