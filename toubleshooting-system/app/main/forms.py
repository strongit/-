# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, SelectMultipleField, SelectField, PasswordField
from wtforms.validators import DataRequired, IPAddress
from wtforms.fields.html5 import IntegerField
from wtforms import widgets

msg = '该字段不能为空'


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# 网络线路表单
class NetLineForm(FlaskForm):
    name = StringField('线路名称', validators=[DataRequired(message=msg)])
    type = SelectField('线路类型', coerce=int, choices=[(1, '基本类型'), (2, '定制类型')],
                       validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')


# 交换机表单
class SwitchForm(FlaskForm):
    description = StringField('描述', validators=[DataRequired(message=msg)])
    ip_address = StringField('IP地址', validators=[DataRequired(message=msg), IPAddress(message='无效的IP地址')])
    cer_id = SelectField('登录凭证', coerce=int, validators=[DataRequired(message=msg)])
    area_id = SelectField('区域', coerce=int, validators=[DataRequired(message=msg)])
    line_id = MultiCheckboxField('线路', coerce=int, validators=[DataRequired(message=msg)])
    level = IntegerField('层级', validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')


# 检测IP表单
class CheckIPForm(FlaskForm):
    ip_address = StringField('IP地址', validators=[DataRequired(message=msg), IPAddress(message='无效的IP地址')])
    submit = SubmitField('检测')


# 区域表单
class AreaForm(FlaskForm):
    name = StringField('区域名称', validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')


# IP地址表单
class IPAddressForm(FlaskForm):
    ip_address = StringField('IP地址', validators=[DataRequired(message=msg)])
    line_id = MultiCheckboxField('线路', coerce=int, validators=[DataRequired(message=msg)])
    area_id = SelectField('区域', coerce=int, validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')


# 登录凭证表单
class CertificateForm(FlaskForm):
    name = StringField('凭证名称', validators=[DataRequired(message=msg)])
    username = StringField('用户名', validators=[DataRequired(message=msg)])
    password = PasswordField('密码', validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')


# 端口扫描表单
class ScanPortForm(FlaskForm):
    ip_address = StringField('IP地址', validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')

