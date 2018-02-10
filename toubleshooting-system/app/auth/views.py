# -*- coding:utf-8 -*-
from . import auth
from ..models import User, Area
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for, flash, abort, current_app
from .forms import AddUserForm, EditUserForm, ChangePasswordForm, AdminChangePasswordForm
from app import db


# 用户登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.values.get('username')
        password = request.values.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.verify_password(password):
                login_user(user, remember=True)
                return redirect(url_for('main.index'))
        flash('用户名或密码错误', 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')


# 用户登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# 用户管理
@auth.route('/users', defaults={'option': 'list', 'user_id': 0}, methods=['GET', 'POST'])
@auth.route('/users/<string:option>', defaults={'user_id': 0}, methods=['GET', 'POST'])
@auth.route('/users/<string:option>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def users(option, user_id):
    if not current_user.is_admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id).paginate(page, per_page=current_app.config['USERS_PER_PAGE'],
                                                       error_out=False)
    users = pagination.items
    if option == 'add':
        form = AddUserForm()
        form.areas.choices = [(a.id, a.name) for a in Area.query.all()]
        if form.validate_on_submit():
            if not User.query.filter_by(username=form.username.data).first():
                new_user = User(username=form.username.data)
                new_user.password = form.password.data
                new_user.areas = [Area.query.get(a) for a in form.areas.data]
                db.session.add(new_user)
                db.session.commit()
                flash('添加用户成功', 'success')
                return redirect(url_for('auth.users', page=page))
            flash('该用户已存在', 'error')
            return redirect(url_for('auth.users', option='add', page=page))
        return render_template('auth/users.html', form=form, page=page)
    if option == 'delete' and user_id:
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            flash('无法删除管理员用户', 'error')
            return redirect(url_for('auth.users'))
        db.session.delete(user)
        db.session.commit()
        flash('删除用户成功', 'success')
        return redirect(url_for('auth.users'))
    if option == 'edit' and user_id:
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            flash('无法修改管理员用户', 'error')
            return redirect(url_for('auth.users', page=page))
        form = EditUserForm()
        form.areas.choices = [(a.id, a.name) for a in Area.query.all()]
        if form.validate_on_submit():
            verify_user = User.query.filter_by(username=form.username.data).first()
            if not verify_user or verify_user == user:
                user.username = form.username.data
                user.areas = [Area.query.get(a) for a in form.areas.data]
                flash('修改用户成功', 'success')
                return redirect(url_for('auth.users', page=page))
            flash('该用户已存在', 'error')
            return redirect(url_for('auth.users', option='edit', user_id=user.id, page=page))
        form.username.data = user.username
        form.areas.data = [a.id for a in user.areas]
        return render_template('auth/users.html', form=form, page=page)
    return render_template('auth/users.html', users=users, pagination=pagination, page=page)


# 修改密码
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            flash('修改密码成功', 'success')
            return redirect(url_for('auth.change_password'))
        flash('原始密码错误', 'error')
        return redirect(url_for('auth.change_password'))
    return render_template('auth/change_password.html', form=form)


# 管理员修改密码
@auth.route('/admin_change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    form = AdminChangePasswordForm()
    form.username.choices = [(u.id, u.username) for u in User.query.all()]
    if form.validate_on_submit():
        user = User.query.get_or_404(int(form.username.data))
        user.password = form.new_password.data
        flash('用户（%s）密码修改成功' % user.username, 'success')
        return redirect(url_for('auth.admin_change_password'))
    return render_template('auth/change_password.html', form=form)

