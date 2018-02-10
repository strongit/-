# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo
from wtforms.fields import PasswordField, SubmitField, StringField, SelectMultipleField, SelectField
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


# 添加用户表单
class AddUserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message=msg)])
    password = PasswordField('密码', validators=[DataRequired(message=msg), EqualTo('confirm_password',
                                                                                  message='两次密码输入不一致')])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(message=msg),
                                                         EqualTo('password', message='两次密码输入不一致')])
    areas = MultiCheckboxField('区域', coerce=int, validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')


# 修改用户表单
class EditUserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message=msg)])
    areas = MultiCheckboxField('区域', coerce=int, validators=[DataRequired(message=msg)])
    submit = SubmitField('提交')


# 修改密码表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('原始密码', validators=[DataRequired(message=msg)])
    new_password = PasswordField('新密码', validators=[DataRequired(message=msg), EqualTo('confirm_password',
                                                                                       message='两次密码输入不一致')])
    confirm_password = PasswordField('确认新密码', validators=[DataRequired(message=msg),
                                                          EqualTo('new_password', message='两次密码输入不一致')])
    submit = SubmitField('提交')


# 管理员修改密码表单
class AdminChangePasswordForm(FlaskForm):
    username = SelectField('用户', coerce=int, validators=[DataRequired(message=msg)])
    new_password = PasswordField('新密码', validators=[DataRequired(message=msg), EqualTo('confirm_password',
                                                                                       message='两次密码输入不一致')])
    confirm_password = PasswordField('确认新密码', validators=[DataRequired(message=msg),
                                                          EqualTo('new_password', message='两次密码输入不一致')])
    submit = SubmitField('提交')
