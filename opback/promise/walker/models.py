# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the model module for the walker package
# holding walker, trail.. etc.
#
from .. import db, app
# from . import utils as walkerUtils
from .. import utils, ma
# from ..ansiAdapter import ShellExecAdapter
from ..user.models import User
from sqlalchemy import and_, or_
import datetime
from sqlalchemy.dialects.mysql import LONGTEXT


class Walker(db.Model):
    """
    shellWalker model
    """
    __tablename__ = 'walker'
    walker_id = db.Column(db.String(64), primary_key=True)
    walker_name = db.Column(db.String(64))
    valid = db.Column(db.SmallInteger)
    # all the trails of this wallker
    trails = db.relationship('Trail', backref='walker', lazy='dynamic')
    shellmission = db.relationship(
        'ShellMission', backref='walker', lazy='select')
    scriptmission = db.relationship(
        'ScriptMission', backref='walker', lazy='dynamic')
    forwardmission = db.relationship(
        'ForwardMission', backref='walker', lazy='dynamic')
    # owner of this walker
    owner_id = db.Column(db.String(64), db.ForeignKey('user.user_id'))
    # state code:
    # Null: has no state yet
    # -2: established
    # -1: running
    #  0: all success
    # >0: num of faild tasks
    # -3: timeout
    # -4: faild to start
    state = db.Column(db.Integer)

    def __repr__(self):
        return '<walker %r>' % self.walker_id

    def __init__(self, walker_name, valid=1):
        self.walker_id = utils.genUuid(walker_name)
        self.walker_name = walker_name
        self.valid = valid

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('save walker ' + self.walker_name + ' to db.')
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    def establish(self, iplist, owner):
        # establish the walker
        self.owner_id = owner.user_id
        self.state = -1
        # establish trails(one target ip with one trail)
        trail_list = []
        for ip in iplist:
            trail = Trail(ip)
            trail.save()
            trail_list.append(trail)

        [msg, state] = self.addTrailList(trail_list)
        if state is not 0:
            return [msg, None]
#                msg = 'walker' + self.walker_id + ' establish faild.'
#                app.logger.warning(utils.logmsg(msg))
#                return [msg, None]
        self.save()
        msg = 'walker' + self.walker_id + ' established'
        app.logger.debug(utils.logmsg(msg))
        return [msg, self.trails.all()]

    def addTrailList(self, trail_list):
        self.trails = trail_list
        try:
            db.session.add(self)
            db.session.commit()
        except:
            msg = 'add trail faild.'
            app.logger.debug(utils.logmsg(msg))
            return [msg, 1]
        msg = 'add trails success.'
        app.logger.debug(utils.logmsg(msg))
        return [msg, 0]

    def getTrails(self):
        trails = self.trails.all()
        json_trails = trails_schema.dump(trails).data
        return [trails, json_trails]

    def getTrailFromIp(self):
        trails = self.trails.first()
        return trails

    def getOwner(self):
        owner = User.query.filter_by(user_id=self.owner_id).first()
        return owner

    @staticmethod
    def getFromUser(user, valid=1):
        walkers = Walker.query.filter_by(owner_id=user.user_id,
                                         valid=valid).all()
        if walkers:
            json_walkers = walkers_schema.dump(walkers).data
            return [walkers, json_walkers]
        else:
            return [None, None]

    @staticmethod
    def getFromWalkerIdWithinUser(walker_id, user, valid=1):
        walker = Walker.query.filter_by(
            walker_id=walker_id, owner_id=user.user_id, valid=valid).first()
        json_walker = walker_schema.dump(walker).data
        return [walker, json_walker]

    @staticmethod
    def getShellMissionWalker(user=None, valid=1):
        if user is not None:
            walkers = db.session.query(Walker).filter(and_(
                Walker.owner_id == user.user_id,
                Walker.valid == valid,
                Walker.shellmission.any())).all()
        else:
            walkers = db.session.query(Walker).filter(and_(
                Walker.valid == valid,
                Walker.shellmission.any())).all()
        if walkers:
            json_walkers = walkers_schema.dump(walkers).data
            return [walkers, json_walkers]
        else:
            return [None, None]

    @staticmethod
    def getScriptMissionWalker(user, valid=1):
        if user:
            walkers = db.session.query(Walker).filter(and_(
                Walker.owner_id == user.user_id,
                Walker.valid == valid,
                Walker.scriptmission.any())).all()
        else:
            walkers = db.session.query(Walker).filter(and_(
                Walker.valid == valid,
                Walker.scriptmission.any())).all()
        if walkers:
            json_walkers = walkers_schema.dump(walkers).data
            return [walkers, json_walkers]
        else:
            return [None, None]

    @staticmethod
    def getForwardMissionWalker(user, valid=1):
        if user:
            walkers = db.session.query(Walker).filter(and_(
                Walker.owner_id == user.user_id,
                Walker.valid == valid,
                Walker.forwardmission.any())).all()
        else:
            walkers = db.session.query(Walker).filter(and_(
                Walker.valid == valid,
                Walker.forwardmission.any())).all()
        if walkers:
            json_walkers = walkers_schema.dump(walkers).data
            return [walkers, json_walkers]
        else:
            return [None, None]


class ShellMission(db.Model):
    """
    shellWalker model
    """
    __tablename__ = 'shellmission'
    shellmission_id = db.Column(db.String(64), primary_key=True)
    shell = db.Column(db.String(256))
    # run the shell as this user on the target hosts
    osuser = db.Column(db.String(64))
    walker_id = db.Column(db.String(64), db.ForeignKey('walker.walker_id'))
    # walker = db.relationship()

    def __repr__(self):
        return '<shellmission %r>' % self.shellmission_id

    def __init__(self, shell, osuser, walker):
        self.shellmission_id = utils.genUuid(shell)
        self.shell = shell
        self.osuser = osuser
        self.walker_id = walker.walker_id

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('save shell mission:' + self.shellmission_id)
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    def getTrails(self):
        walker = self.getWalker()
        [trails, json_trails] = walker.getTrails()
        return [trails, json_trails]

    def getWalker(self):
        walker = Walker.query.filter_by(walker_id=self.walker_id).first()
        return walker

    def getOwner(self):
        walker = self.walker(self)
        owner = User.getValidUser(user_id=walker.owner_id)
        return owner

    def getIplist(self):
        iplist = list()
        [trails, json_trails] = self.getTrails()
        for trail in trails:
            iplist.append(trail.ip)
        return iplist


class ScriptMission(db.Model):
    """
    scriptWalker model
    """
    __tablename__ = 'scriptmission'
    scriptmission_id = db.Column(db.String(64), primary_key=True)
    script_id = db.Column(db.String(64), db.ForeignKey('script.script_id'))
    params = db.Column(db.String(512))
    # run the script as this user on the target hosts
    osuser = db.Column(db.String(64))
    walker_id = db.Column(db.String(64), db.ForeignKey('walker.walker_id'))
    # walker = db.relationship()

    def __repr__(self):
        return '<scriptmission %r>' % self.scriptmission_id

    def __init__(self, script, osuser, params, walker):
        self.scriptmission_id = utils.genUuid(str(script.script_name))
        self.script_id = script.script_id
        self.osuser = osuser
        self.params = params
        self.walker_id = walker.walker_id

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('save script mission:' + self.scriptmission_id)
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    def getScript(self, valid=1):
        script = Script.query.filter_by(
            script_id=self.script_id, valid=valid).first()
        return script

    def getTrails(self):
        walker = self.getWalker()
        [trails, json_trails] = walker.getTrails()
        return [trails, json_trails]

    def getWalker(self):
        walker = Walker.query.filter_by(walker_id=self.walker_id).first()
        return walker

    def getOwner(self):
        walker = self.walker(self)
        owner = User.getValidUser(user_id=walker.owner_id)
        return owner

    def getIplist(self):
        iplist = list()
        [trails, json_trails] = self.getTrails()
        for trail in trails:
            iplist.append(trail.ip)
        return iplist


class ForwardMission(db.Model):
    """
    forward Walker model
    """
    __tablename__ = 'forwardmission'
    forwardmission_id = db.Column(db.String(64), primary_key=True)
    script_id = db.Column(db.String(64), db.ForeignKey('script.script_id'))
    params = db.Column(db.String(512))
    walker_id = db.Column(db.String(64), db.ForeignKey('walker.walker_id'))
    # run the script as this user on the target equipment
    osuser = db.Column(db.String(64))
    stdout = db.Column(LONGTEXT)
    # walker = db.relationship()

    def __repr__(self):
        return '<forwardmission %r>' % self.forwardmission_id

    def __init__(self, script, osuser, params, walker):
        self.forwardmission_id = utils.genUuid(str(script.script_name))
        self.script_id = script.script_id
        self.params = params
        self.walker_id = walker.walker_id

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg(
                'save forward mission:' + self.forwardmission_id)
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    def getScript(self, valid=1):
        script = Script.query.filter_by(
            script_id=self.script_id, valid=valid).first()
        return script

    def getTrails(self):
        walker = self.getWalker()
        [trails, json_trails] = walker.getTrails()
        return [trails, json_trails]

    def getWalker(self):
        walker = Walker.query.filter_by(walker_id=self.walker_id).first()
        return walker

    def getOwner(self):
        walker = self.walker(self)
        owner = User.getValidUser(user_id=walker.owner_id)
        return owner

    def getIplist(self):
        iplist = list()
        [trails, json_trails] = self.getTrails()
        for trail in trails:
            iplist.append(trail.ip)
        return iplist


class Script(db.Model):
    '''
    script for script mission
    '''
    __tablename__ = 'script'
    script_id = db.Column(db.String(64), primary_key=True)
    script_name = db.Column(db.String(64))
    script_text = db.Column(db.Text)
    owner_id = db.Column(db.String(64), db.ForeignKey('user.user_id'))
    time_create = db.Column(db.DATETIME)
    time_last_edit = db.Column(db.DATETIME)
    # languages of scripts may be : 1.shell  2.python
    script_lang = db.Column(db.String(32))
    is_public = db.Column(db.SmallInteger)
    valid = db.Column(db.SmallInteger)
    # script_type may be : "ansible":1; "forward":2
    # default:1
    script_type = db.Column(db.SmallInteger)

    def __repr__(self):
        return '<script %r>' % self.script_id

    def __init__(self, script_name, script_text, owner,
                 script_lang, is_public, script_type=1, valid=1):
        self.script_id = utils.genUuid(script_name)
        self.script_name = script_name
        self.script_text = script_text
        self.owner_id = owner.user_id
        self.script_lang = script_lang
        self.time_create = datetime.datetime.now()
        self.time_last_edit = self.time_create
        self.last_edit_owner_id = self.owner_id
        self.is_public = is_public
        self.valid = valid
        self.script_type = script_type

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('save script:' + self.script_id)
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    @staticmethod
    def getFromIdWithinUser(script_id, user, valid=1):
        script = Script.query.filter_by(
            script_id=script_id,
            valid=valid,
            owner_id=user.user_id).first()
        if script:
            json_script = script_schema.dump(script).data
            return [script, json_script]
        else:
            return [None, None]

    @staticmethod
    def getFromIdWithinUserOrPublic(script_id, user, valid=1):
        script = Script.query.filter(
            and_(
                Script.script_id == script_id,
                Script.valid == valid,
                or_(
                    Script.owner_id == user.user_id,
                    Script.is_public == 1))).first()
        return script

    @staticmethod
    def getWithinUser(user, valid=1, script_type=None):
        if script_type is None:
            scripts = Script.query.filter_by(
                owner_id=user.user_id, valid=valid).all()
        else:
            scripts = Script.query.filter_by(
                owner_id=user.user_id, valid=valid, script_type=script_type)
        if scripts:
            json_scripts = scripts_schema.dump(scripts).data
            return [scripts, json_scripts]
        else:
            return [None, None]

    def update(self, script_name, script_text, script_lang, edit_user,
               is_public, script_type):
        self.script_name = script_name
        self.script_text = script_text
        self.script_lang = script_lang
        self.time_last_edit = datetime.datetime.now()
        self.is_public = is_public
        self.script_type = script_type

    def setInvalid(self):
        self.valid = 0
        try:
            self.save()
            msg = 'script<id:' + self.script_id + '> deleted.'
            state = True
        except:
            msg = 'script<id:' + self.script_id + '> faild to delete.'
            state = False
        return [state, msg]

    @staticmethod
    def getCallableScripts(user, script_id=None, script_type=None, valid=1):
        if script_id is None:
            if script_type is None:
                scriptUserList = db.session.query(
                    Script, User).join(User).filter(
                    and_(
                        or_(Script.owner_id == user.user_id,
                            Script.is_public == 1),
                        Script.valid == valid)).all()
            else:
                scriptUserList = db.session.query(
                    Script, User).join(User).filter(
                    and_(
                        or_(Script.owner_id == user.user_id,
                            Script.script_type == script_type,
                            Script.is_public == 1),
                        Script.valid == valid)).all()
            return scriptUserList
        else:
            scriptUserInfo = db.session.query(
                Script, User).join(User).filter(
                and_(
                    or_(Script.owner_id == user.user_id,
                        Script.is_public == 1),
                    Script.script_id == script_id,
                    Script.valid == valid)).first()
            return scriptUserInfo


class Trail(db.Model):
    '''
    a trail stores the result of task running on ONE host
    '''
    __tablename__ = 'trail'
    trail_id = db.Column(db.String(64), primary_key=True)
    ip = db.Column(db.String(15))
    stdout = db.Column(LONGTEXT)
    stderr = db.Column(LONGTEXT)
    msg = db.Column(db.Text)
    time_start = db.Column(db.DATETIME)
    time_end = db.Column(db.DATETIME)
    time_delta_string = db.Column(db.String(64))

    # result summerize of one trail：
    # comes from ansible.taskqueuemanage._stats.summarize
    sum_ok = db.Column(db.Integer)
    sum_unreachable = db.Column(db.Integer)
    sum_skipped = db.Column(db.Integer)
    sum_changed = db.Column(db.Integer)
    sum_failures = db.Column(db.Integer)

    walker_id = db.Column(db.String(64), db.ForeignKey('walker.walker_id'))

    def __repr__(self):
        return '<trail %r>' % self.trail_id

    def __init__(self, ip, stdout=None, state=-2):
        self.trail_id = utils.genUuid(str(ip))
        self.ip = ip
        self.stdout = stdout
        self.state = state

    def resultUpdate(self, stat_sum, result):
        # update the status sum
        self.sum_ok = stat_sum['ok']
        self.sum_unreachable = stat_sum['unreachable']
        self.sum_skipped = stat_sum['skipped']
        self.sum_changed = stat_sum['changed']
        self.sum_failures = stat_sum['failures']
        # update the result
        if 'msg' in result:
            self.msg = result['msg']
        if 'stdout' in result:
            self.stdout = result['stdout']
        if 'stderr' in result:
            self.stderr = result['stderr']
        if 'delta' in result:
            self.time_delta_string = result['delta']
        if 'start' in result:
            self.time_start = datetime.datetime.strptime(
                result['start'], "%Y-%m-%d %H:%M:%S.%f")
        if 'end' in result:
            self.time_end = datetime.datetime.strptime(
                result['end'], "%Y-%m-%d %H:%M:%S.%f")

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('save trail:' + self.trail_id)
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False

            # close db.session, reconnect and try again
            db.session.close()
            db.session.add(self)
            try:
                db.session.commit()
                msg = utils.logmsg('save trail:' + self.trail_id)
                app.logger.debug(msg)
                state = True
            except Exception, e:
                db.session.rollback()
                msg = utils.logmsg('exception: %s.' % e)
                app.logger.info(msg)
                state = False

        return [state, msg]


#####################################################################
#    establish a meta data class for data print                     #
#####################################################################
class WalkerSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Walker
        fields = ['walker_id', 'walker_name', 'state']
walker_schema = WalkerSchema()
walkers_schema = WalkerSchema(many=True)


class TrailSchema(ma.ModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Trail
        fields = [
            'trail_id', 'ip', 'sum_ok', 'sum_unreachable',
            'sum_skipped', 'sum_changed', 'sum_failures', 'msg', 'stdout',
            'time_start', 'time_end', 'time_delta_string', 'stderr']
trail_schema = TrailSchema()
trails_schema = TrailSchema(many=True)


class ScriptSchema(ma.ModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Script
        fields = [
            'script_id', 'script_name', 'time_last_edit', 'script_text']

script_schema = ScriptSchema()
scripts_schema = ScriptSchema(many=True)
