# -*- coding:utf-8 -*-
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# 用户区域关系表
users_to_areas = db.Table('users_to_areas',
                          db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                          db.Column('area_id', db.Integer, db.ForeignKey('areas.id'))
                          )


# 用户表
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    areas = db.relationship('Area', secondary=users_to_areas, backref=db.backref('users', lazy='dynamic'))

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# 线路交换机关系表
lines_to_switchs = db.Table('lines_to_switchs',
                            db.Column('line_id', db.Integer, db.ForeignKey('lines.id')),
                            db.Column('switch_id', db.Integer, db.ForeignKey('switchs.id')))


# 线路IP地址关系表
lines_to_ipaddresses = db.Table('lines_to_ipaddresses',
                                db.Column('line_id', db.Integer, db.ForeignKey('lines.id')),
                                db.Column('ipaddress_id', db.Integer, db.ForeignKey('ip_addresses.id')))


# 线路表
class Line(db.Model):
    __tablename__ = 'lines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    type = db.Column(db.Integer, default=1)
    custom_switchs = db.Column(db.String(128))


# 交换机表
class Switch(db.Model):
    __tablename__ = 'switchs'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128))
    ip_address = db.Column(db.String(128), unique=True)
    level = db.Column(db.Integer)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    cer_id = db.Column(db.Integer, db.ForeignKey('certificates.id'))
    lines = db.relationship('Line', secondary=lines_to_switchs, backref=db.backref('switchs', lazy='dynamic'))


# 区域表
class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    ipaddresses = db.relationship('IPAddress', backref='area', lazy='dynamic')
    switchs = db.relationship('Switch', backref='area', lazy='dynamic')


# 业务IP地址表
class IPAddress(db.Model):
    __tablename__ = 'ip_addresses'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(128), unique=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
    lines = db.relationship('Line', secondary=lines_to_ipaddresses, backref=db.backref('ip_addresses', lazy='dynamic'))


# 登录凭证表
class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    username = db.Column(db.String(128))
    password = db.Column(db.String(128))
    switchs = db.relationship('Switch', backref='certificate', lazy='dynamic')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
