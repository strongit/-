# -*- coding:utf-8 -*-
import sys
sys.path.append('.')

from flask.ext.script import Manager, Shell, prompt_bool
from flask.ext.migrate import Migrate, MigrateCommand

from promise import app, db
from promise.user import utils as userUtils
from promise.user.models import User, Privilege, Role
from promise.eater.models import ITModel, Connection, OSUser

migrate = Migrate(app, db)

manager = Manager(app, usage="Perform database operations")

manager.add_command('db', MigrateCommand)

default_bind_key = '__all__'


@manager.command
def initdb(bind=default_bind_key):
    "initialize database tables"
    import os
    if not os.path.exists(app.config['DB_FOLDER']):
        os.mkdir(app.config['DB_FOLDER'])
    db.create_all(bind=bind)
    if bind == '__all__':
        print 'Database inited, location:\r\n[%-10s] %s' % (
            'DEFAULT', app.config['SQLALCHEMY_DATABASE_URI'], )
        for k, w in app.config['SQLALCHEMY_BINDS'].items():
            print '[%-10s] %s' % (k.upper(), w)
    elif bind is None:
        print 'Database inited, location:\r\n[%-10s] %s' % (
            'DEFAULT', app.config['SQLALCHEMY_DATABASE_URI'], )
    elif bind in app.config['SQLALCHEMY_BINDS'].keys():
        print 'Database inited, location:\r\n[%-10s] %s' % (
            bind.upper(), app.config['SQLALCHEMY_BINDS'][bind], )
    else:
        print 'Unknown database: [%+10s].' % bind.upper()


@manager.command
def importdata():
    "Import data into database tables"
    user_admin_privilege = Privilege(
        privilege_name='userAdmin',
        description='user/role/privlilege administration.')
    inventory_admin_privilege = Privilege(
        privilege_name='inventoryAdmin',
        description='cmdb/inventory administration')
    shell_exec_privilege = Privilege(
        privilege_name='shellExec',
        description='execution of shell module of walker.')
    script_exec_privilege = Privilege(
        privilege_name='scriptExec',
        description='execution of script module of walker.')
    walker_info_privilege = Privilege(
        privilege_name='walkerInfo',
        description='get the details infomation of walkers.')
    forward_exec_privilege = Privilege(
        privilege_name='forwardExec',
        description='execution of forward module of walker.')
    user_admin_privilege.save()
    inventory_admin_privilege.save()
    shell_exec_privilege.save()
    script_exec_privilege.save()
    walker_info_privilege.save()
    forward_exec_privilege.save()
    # init roles
    role_root = Role(role_name='root', description='超级用户')
    role_operator = Role(role_name='operator', description='运维操作员')
    role_inventory_admin = Role(
        role_name='inventoryAdmin', description='资源管理员')
    role_user_admin = Role(role_name='userAdmin', description='用户管理员')
    role_network_operator = Role(
        role_name='networkoperator', description='网络运维操作员')
    role_root.update(
        privileges=[
            inventory_admin_privilege, user_admin_privilege,
            shell_exec_privilege, script_exec_privilege,
            walker_info_privilege, forward_exec_privilege])
    role_user_admin.update(privileges=[user_admin_privilege])
    role_inventory_admin.update(privileges=[inventory_admin_privilege])
    role_operator.update(
        privileges=[
            shell_exec_privilege, script_exec_privilege,
            walker_info_privilege])
    role_network_operator.update(privileges=[forward_exec_privilege])
    role_root.save()
    role_user_admin.save()
    role_inventory_admin.save()
    role_operator.save()
    role_network_operator.save()
    # init users
    user1 = User(
        username='tom',
        hashed_password=userUtils.hash_pass("tompass"),
        role_list=[role_operator])
    user2 = User(
        username='jerry',
        hashed_password=userUtils.hash_pass("jerrypass"),
        role_list=[role_inventory_admin])
    user3 = User(
        username='mike',
        hashed_password=userUtils.hash_pass("mikepass"),
        role_list=[role_user_admin])
    user4 = User(
        username='john',
        hashed_password=userUtils.hash_pass("johnpass"),
        role_list=[role_operator, role_network_operator])
    # user2.addRole(role=roleInventoryAdmin)
    root_user = User(
        username=app.config['DEFAULT_ROOT_USERNAME'],
        hashed_password=userUtils.hash_pass(
            app.config['DEFAULT_ROOT_PASSWORD']),
        role_list=[role_root])
    visitor = User(
        username='visitor',
        hashed_password=userUtils.hash_pass('visitor'))
    user1.save()
    user2.save()
    user3.save()
    user4.save()
    root_user.save()
    visitor.save()
    # init eater
    eater_importdata()
    print 'Data imported'


@manager.command
def dropdb(bind=default_bind_key):
    "Drops database tables"
    if prompt_bool(
        "Are you sure you want to lose all your data in bind `%s`" % (
            bind.upper(), )):
        db.drop_all(bind=bind)
        if bind == '__all__':
            print 'Database dropped, location:\r\n[%-10s] %s' % (
                'DEFAULT', app.config['SQLALCHEMY_DATABASE_URI'], )
            for k, w in app.config['SQLALCHEMY_BINDS'].items():
                print '[%-10s] %s' % (k.upper(), w)
        elif bind is None:
            print 'Database dropped, location:\r\n[%-10s] %s' % (
                'DEFAULT', app.config['SQLALCHEMY_DATABASE_URI'], )
        elif bind in app.config['SQLALCHEMY_BINDS'].keys():
            print 'Database dropped, location:\r\n[%-10s] %s' % (
                bind.upper(), app.config['SQLALCHEMY_BINDS'][bind], )
        else:
            print 'Unknown database: [%+10s].' % bind.upper()


@manager.command
def recreatedb():
    "Recreates database tables \
    (same as issuing 'drop', 'create' and then 'import')"
    dropdb()
    initdb()
    importdata()


@manager.command
def systemupdate():
    "for system update."
    initdb()
    db.engine.execute("ALTER TABLE script ADD script_type smallint;")
    db.engine.execute("UPDATE script SET script_type=1;")
    # print result.context.__dict__
    forward_exec_privilege = Privilege(
        privilege_name='forwardExec',
        description='execution of forward module of walker.')
    forward_exec_privilege.save()

    role_operator = Role.getValidRole(role_name='operator')
    role_network_operator = Role(
        role_name='networkoperator', description='网络运维操作员')
    # role_network_operator = Role.getValidRole(role_name='networkoperator')
    role_network_operator.update(
        privileges=[forward_exec_privilege])
    role_network_operator.save()
    user4 = User(
        username='john',
        hashed_password=userUtils.hash_pass("johnpass"),
        role_list=[role_network_operator, role_operator])
    user4.save()


@manager.command
def eater_importdata():
    "import data to eater"
    # init it model
    model = ITModel()
    model.insert(name='bclinux7', vender='bclinux7', id='m-0000')
    model.insert(name='sr7750', vender='bel', id='m-0001')
    model.insert(name='asa', vender='Cisco', id='m-0002')
    model.insert(name='asr1006', vender='Cisco', id='m-0003')
    model.insert(name='c2960', vender='Cisco', id='m-0004')
    model.insert(name='c4510', vender='Cisco', id='m-0005')
    model.insert(name='c6509', vender='Cisco', id='m-0006')
    model.insert(name='n5548', vender='Cisco', id='m-0007')
    model.insert(name='n5596', vender='Cisco', id='m-0008')
    model.insert(name='n7010', vender='Cisco', id='m-0009')
    model.insert(name='n7018', vender='Cisco', id='m-0010')
    model.insert(name='n7710', vender='cisco', id='m-0011')
    model.insert(name='n7718', vender='cisco', id='m-0012')
    model.insert(name='fw1000', vender='depp', id='m-0013')
    model.insert(name='m6000', vender='depp', id='m-0014')
    model.insert(name='f510000', vender='f5', id='m-0015')
    model.insert(name='s5800', vender='fenghuo', id='m-0016')
    model.insert(name='fg3040', vender='Fortinet', id='m-0017')
    model.insert(name='fg3950', vender='Fortinet', id='m-0018')
    model.insert(name='e8000e', vender='huawei', id='m-0019')
    model.insert(name='s9303', vender='Huawei', id='m-0020')
    model.insert(name='s9312', vender='huawei', id='m-0021')
    model.insert(name='mx960', vender='Juniper', id='m-0022')
    model.insert(name='s3300', vender='Maipu', id='m-0023')
    model.insert(name='usg1000', vender='Qimingxingchen', id='m-0024')
    model.insert(name='r3048g', vender='raisecom', id='m-0025')
    model.insert(name='af6020', vender='sinfor', id='m-0026')
    model.insert(name='m6000', vender='zte', id='m-0027')
    # init connection
    connect = Connection()
    connect.insert(method='ssh', port=22, id='conn-0001')
    connect.insert(method='telnet', port=23, id='conn-0002')
    # init os user
    osuser = OSUser()
    connect1 = Connection.query.filter_by(id='conn-0001').first()
    connect2 = Connection.query.filter_by(id='conn-0002').first()
    osuser.insert(
        id='u-0001', name='python_script',
        con_pass='50526d5765504b52ad9234f8c6723e5352d966203cd701401a006955abf8'
                 '92e6fa5d88e4a740fc95c4b33dad17518c825dafb65c9ad891ed90d1634f'
                 '532b55b1249f821a2e8480b22aa25350673cdd75b15d9cf3bf156d79168e'
                 '552ffa3a362f9bf6af5b1af1a79c22cd3d8f9b8e42806ea95227613b5f5c'
                 '7b298375a4563199',
        connect=[connect1, connect2])
    osuser.insert(
        id='u-0002', name='python_script',
        con_pass='4a6f9a31a1033319f3bf3852c8eef2ce62c607c5d40b50670234a2ea72ca'
                 'af77668f34a4f32c422be4f107071c370cde9c9b872134414674fe8f457c'
                 'a2489fd55b5e2b637d0536ba5dc42815b55ed4a83eb1603b0af7edc8f5cc'
                 '4549f58344e724cb602dadbc39d1183cd50a16aa56da0ac4aaba1638e2d1'
                 '80c053212e33a680',
        connect=[connect1])
    osuser.insert(
        id='u-0003', name='admin',
        con_pass='50526d5765504b52ad9234f8c6723e5352d966203cd701401a006955abf8'
                 '92e6fa5d88e4a740fc95c4b33dad17518c825dafb65c9ad891ed90d1634f'
                 '532b55b1249f821a2e8480b22aa25350673cdd75b15d9cf3bf156d79168e'
                 '552ffa3a362f9bf6af5b1af1a79c22cd3d8f9b8e42806ea95227613b5f5c'
                 '7b298375a4563199',
        connect=[connect1])
    osuser.insert(
        id='u-0004', name='wangluozu',
        con_pass='5269742d141b86c0856012d2ba344c736a54ec85df77f93a0d433e9827fb'
                 '259f0355dec6ab5a09698b2cdfcdf84acf0b8cbcef4ea9b8da6c9699f2ed'
                 '748d90af987000878b1c1581301af2c1e9d638432f46c3ac5f8e65dd640a'
                 '63d32699cf16d8f4b20932f5cf2b68d39a1c33276c88f2d579137e8f593a'
                 '28f194eaa7f1d407',
        connect=[connect1])


@manager.command
def eater_recreatedb():
    "recreate database for eater"
    dropdb(bind='eater')
    initdb()
    eater_importdata()


def _make_context():
    return dict(app=app, db=db)

manager.add_command("shell", Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
