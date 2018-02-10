# -*- coding:utf-8 -*-
from . import main
from flask import render_template, current_app, send_from_directory, redirect, request, flash, url_for, jsonify, abort
from flask_login import login_required
from ..models import Line, Switch, Area, IPAddress, Certificate
from .forms import NetLineForm, SwitchForm, CheckIPForm, AreaForm, IPAddressForm, CertificateForm, ScanPortForm
from app import db, redis_store
from ..tasks import remote_ping, portscanner
from ..tools import get_ips
import os
import re


# 首页
@main.route('/')
@login_required
def index():
    return redirect(url_for('main.check_ip'))


# 图标
@main.route('/favicon.ico')
def favicon():
    app = current_app._get_current_object()
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# 网络线路管理
@main.route('/netlines', defaults={'option': 'list', 'line_id': 0})
@main.route('/netlines/<string:option>', defaults={'line_id': 0}, methods=['GET', 'POST'])
@main.route('/netlines/<string:option>/<int:line_id>', methods=['GET', 'POST'])
@login_required
def netlines(option, line_id):
    page = request.args.get('page', 1, type=int)
    pagination = Line.query.order_by(Line.id).paginate(page, per_page=current_app.config['LINES_PER_PAGE'],
                                                       error_out=False)
    lines = pagination.items
    switchs_option = [(s.id, s.description) for s in Switch.query.all()]
    if option == 'add':
        form = NetLineForm()
        if form.validate_on_submit():
            if not Line.query.filter_by(name=form.name.data).first():
                custom_switchs = ''
                if form.type.data == 2:
                    custom_switchs_list = []
                    for key in request.values:
                        if re.match(r'^select\d+$', key):
                            custom_switchs_list.append((key, request.values.get(key)))
                    custom_switchs = ','.join([v[1] for v in sorted(custom_switchs_list, key=lambda x: int(x[0][6:]))])
                new_line = Line(name=form.name.data, type=form.type.data, custom_switchs=custom_switchs)
                db.session.add(new_line)
                db.session.commit()
                flash('添加线路成功', 'success')
                return redirect(url_for('main.netlines', page=page))
            flash('该线路已存在', 'error')
            return redirect(url_for('main.netlines', option='add', page=page))
        return render_template('main/netlines.html', form=form, page=page, switchs_option=switchs_option)
    if option == 'delete' and line_id:
        line = Line.query.get_or_404(line_id)
        for switch in Switch.query.all():
            if line in switch.lines:
                flash('该线路已经被使用，无法删除', 'error')
                return redirect(url_for('main.netlines', page=page))
        db.session.delete(line)
        db.session.commit()
        flash('删除线路成功', 'success')
        return redirect(url_for('main.netlines'))
    if option == 'edit' and line_id:
        line = Line.query.get_or_404(line_id)
        form = NetLineForm()
        if form.validate_on_submit():
            verify_line = Line.query.filter_by(name=form.name.data).first()
            if not verify_line or verify_line == line:
                custom_switchs = ''
                if form.type.data == 2:
                    custom_switchs_list = []
                    for key in request.values:
                        if re.match(r'^select\d+$', key):
                            custom_switchs_list.append((key, request.values.get(key)))
                    custom_switchs = ','.join([v[1] for v in sorted(custom_switchs_list, key=lambda x: int(x[0][6:]))])
                line.name = form.name.data
                line.type = form.type.data
                line.custom_switchs = custom_switchs
                flash('修改线路成功', 'success')
                return redirect(url_for('main.netlines', page=page))
            flash('该线路已存在', 'error')
            return redirect(url_for('main.netlines', option='edit', line_id=line.id, page=page))
        form.name.data = line.name
        form.type.data = line.type
        return render_template('main/netlines.html', form=form, page=page, switchs_option=switchs_option,
                               custom_switchs=line.custom_switchs.split(','))
    return render_template('main/netlines.html', lines=lines, pagination=pagination, page=page)


# 交换机管理
@main.route('/switchs', defaults={'option': 'list', 'switch_id': 0})
@main.route('/switchs/<string:option>', defaults={'switch_id': 0}, methods=['GET', 'POST'])
@main.route('/switchs/<string:option>/<int:switch_id>', methods=['GET', 'POST'])
@login_required
def switchs(option, switch_id):
    page = request.args.get('page', 1, type=int)
    pagination = Switch.query.order_by(Switch.id).\
        paginate(page, per_page=current_app.config['SWITCHS_PER_PAGE'], error_out=False)
    switchs = pagination.items
    line_choices = [(l.id, l.name) for l in Line.query.filter_by(type=1).all()]
    area_choices = [(a.id, a.name) for a in Area.query.all()]
    cer_choices = [(c.id, c.name) for c in Certificate.query.all()]
    if option == 'add':
        form = SwitchForm()
        form.line_id.choices = line_choices
        form.area_id.choices = area_choices
        form.cer_id.choices = cer_choices
        if form.validate_on_submit():
            if not Switch.query.filter_by(ip_address=form.ip_address.data).first():
                new_switch = Switch(description=form.description.data, ip_address=form.ip_address.data,
                                    area_id=form.area_id.data, cer_id=form.cer_id.data,
                                    level=form.level.data)
                new_switch.lines = [Line.query.get_or_404(line_id) for line_id in form.line_id.data]
                db.session.add(new_switch)
                db.session.commit()
                flash('添加交换机成功', 'success')
                return redirect(url_for('main.switchs', page=page))
            flash('该交换机已存在', 'error')
            return redirect(url_for('main.switchs', option='add', page=page))
        return render_template('main/switchs.html', form=form, page=page)
    if option == 'delete' and switch_id:
        switch = Switch.query.get_or_404(switch_id)
        db.session.delete(switch)
        db.session.commit()
        flash('删除交换机成功', 'success')
        return redirect(url_for('main.switchs'))
    if option == 'edit' and switch_id:
        switch = Switch.query.get_or_404(switch_id)
        form = SwitchForm()
        form.line_id.choices = line_choices
        form.area_id.choices = area_choices
        form.cer_id.choices = cer_choices
        if form.validate_on_submit():
            verify_switch = Switch.query.filter_by(ip_address=form.ip_address.data).first()
            if not verify_switch or verify_switch == switch:
                switch.description = form.description.data
                switch.ip_address = form.ip_address.data
                switch.area_id = form.area_id.data
                switch.cer_id = form.cer_id.data
                switch.lines = [Line.query.get_or_404(line_id) for line_id in form.line_id.data]
                switch.level = form.level.data
                flash('修改交换机成功', 'success')
                return redirect(url_for('main.switchs', page=page))
            flash('该交换机已存在', 'error')
            return redirect(url_for('main.switchs', option='edit', switch_id=switch.id, page=page))
        form.description.data = switch.description
        form.ip_address.data = switch.ip_address
        form.area_id.data = switch.area_id
        form.cer_id.data = switch.cer_id
        form.line_id.data = [line.id for line in switch.lines]
        form.level.data = switch.level
        return render_template('main/switchs.html', form=form, page=page)
    return render_template('main/switchs.html', switchs=switchs, pagination=pagination, page=page)


# IP检测
@main.route('/check_ip', methods=['GET', 'POST'])
@login_required
def check_ip():
    ip_address = request.args.get('ip_address', '', type=str)
    form = CheckIPForm()
    if form.validate_on_submit():
        if not IPAddress.query.filter_by(ip_address=form.ip_address.data).first():
            flash('该IP为外部IP，暂不支持查询', 'warning')
            return redirect(url_for('main.check_ip'))
        return redirect(url_for('main.check_ip', ip_address=form.ip_address.data))
    form.ip_address.data = ip_address
    if ip_address != '':
        redis_store.delete('check_ip_%s' % ip_address)
        ip = IPAddress.query.filter_by(ip_address=ip_address).first()
        for line in ip.lines:
            if line.type == 1:
                switchs_in_line = [switch for switch in Switch.query.filter_by(area_id=ip.area_id).all()
                                   if line in switch.lines]
            else:
                switchs_in_line = [Switch.query.get(switch_id) for switch_id in line.custom_switchs.split(',')]
            for switch in switchs_in_line:
                remote_ping.delay(ip_address, switch.ip_address, switch.certificate.username,
                                  switch.certificate.password, line.id, switch.id)
        flash('IP检测中，请注意查看下方结果', 'success')
        return render_template('main/check_ip.html', form=form)
    return render_template('main/check_ip.html', form=form)


# 区域管理
@main.route('/areas', defaults={'option': 'list', 'area_id': 0})
@main.route('/areas/<string:option>', defaults={'area_id': 0}, methods=['GET', 'POST'])
@main.route('/areas/<string:option>/<int:area_id>', methods=['GET', 'POST'])
@login_required
def areas(option, area_id):
    page = request.args.get('page', 1, type=int)
    pagination = Area.query.order_by(Area.id).paginate(page, per_page=current_app.config['AREAS_PER_PAGE'],
                                                       error_out=False)
    areas = pagination.items
    if option == 'add':
        form = AreaForm()
        if form.validate_on_submit():
            if not Area.query.filter_by(name=form.name.data).first():
                new_area = Area(name=form.name.data)
                db.session.add(new_area)
                db.session.commit()
                flash('添加区域成功', 'success')
                return redirect(url_for('main.areas', page=page))
            flash('该区域已存在', 'error')
            return redirect(url_for('main.areas', option='add', page=page))
        return render_template('main/areas.html', form=form, page=page)
    if option == 'delete' and area_id:
        if Switch.query.filter_by(area_id=area_id).first() or IPAddress.query.filter_by(area_id=area_id).first():
            flash('该区域已经被使用，无法删除', 'error')
            return redirect(url_for('main.areas', page=page))
        area = Area.query.get_or_404(area_id)
        db.session.delete(area)
        db.session.commit()
        flash('删除区域成功', 'success')
        return redirect(url_for('main.areas'))
    if option == 'edit' and area_id:
        area = Area.query.get_or_404(area_id)
        form = AreaForm()
        if form.validate_on_submit():
            verify_area = Area.query.filter_by(name=form.name.data).first()
            if not verify_area or verify_area == area:
                area.name = form.name.data
                flash('修改区域成功', 'success')
                return redirect(url_for('main.areas', page=page))
            flash('该区域已存在', 'error')
            return redirect(url_for('main.areas', option='edit', area_id=area.id, page=page))
        form.name.data = area.name
        return render_template('main/areas.html', form=form, page=page)
    return render_template('main/areas.html', areas=areas, pagination=pagination, page=page)


# IP地址管理
@main.route('/ip_addresses', defaults={'option': 'list', 'ipaddr_id': 0})
@main.route('/ip_addresses/<string:option>', defaults={'ipaddr_id': 0}, methods=['GET', 'POST'])
@main.route('/ip_addresses/<string:option>/<int:ipaddr_id>', methods=['GET', 'POST'])
@login_required
def ip_addresses(option, ipaddr_id):
    page = request.args.get('page', 1, type=int)
    pagination = IPAddress.query.order_by(IPAddress.id).paginate(page, per_page=current_app.config['IPADDRS_PER_PAGE'],
                                                                 error_out=False)
    ipaddrs = pagination.items
    line_choices = [(l.id, l.name) for l in Line.query.all()]
    area_choices = [(a.id, a.name) for a in Area.query.all()]
    if option == 'add':
        form = IPAddressForm()
        form.line_id.choices = line_choices
        form.area_id.choices = area_choices
        if form.validate_on_submit():
            ips = get_ips(form.ip_address.data)
            if not ips:
                flash('请填写正确的IP地址', 'error')
                return redirect(url_for('main.ip_addresses', page=page))
            for ip_address in ips:
                if not IPAddress.query.filter_by(ip_address=ip_address).first():
                    new_ipaddr = IPAddress(ip_address=ip_address, area_id=form.area_id.data)
                    new_ipaddr.lines = [Line.query.get_or_404(line_id) for line_id in form.line_id.data]
                    db.session.add(new_ipaddr)
                    db.session.commit()
                else:
                    flash('IP：%s已存在，已忽略' % ip_address, 'warning')
            flash('添加IP成功', 'success')
            return redirect(url_for('main.ip_addresses', page=page))
        return render_template('main/ip_addresses.html', form=form, page=page)
    if option == 'delete' and ipaddr_id:
        ipaddr = IPAddress.query.get_or_404(ipaddr_id)
        db.session.delete(ipaddr)
        db.session.commit()
        flash('删除IP成功', 'success')
        return redirect(url_for('main.ip_addresses'))
    if option == 'edit' and ipaddr_id:
        ipaddr = IPAddress.query.get_or_404(ipaddr_id)
        form = IPAddressForm()
        form.line_id.choices = line_choices
        form.area_id.choices = area_choices
        if form.validate_on_submit():
            verify_ipaddr = IPAddress.query.filter_by(ip_address=form.ip_address.data).first()
            if not verify_ipaddr or verify_ipaddr == ipaddr:
                ipaddr.ip_address = form.ip_address.data
                ipaddr.area_id = form.area_id.data
                ipaddr.lines = [Line.query.get_or_404(line_id) for line_id in form.line_id.data]
                flash('修改IP成功', 'success')
                return redirect(url_for('main.ip_addresses', page=page))
            flash('该IP已存在', 'error')
            return redirect(url_for('main.ip_addresses', option='edit', ipaddr_id=ipaddr.id, page=page))
        form.ip_address.data = ipaddr.ip_address
        form.area_id.data = ipaddr.area_id
        form.line_id.data = [line.id for line in ipaddr.lines]
        return render_template('main/ip_addresses.html', form=form, page=page)
    return render_template('main/ip_addresses.html', ipaddrs=ipaddrs, pagination=pagination, page=page)


# 登录凭证管理
@main.route('/certificates', defaults={'option': 'list', 'cer_id': 0})
@main.route('/certificates/<string:option>', defaults={'cer_id': 0}, methods=['GET', 'POST'])
@main.route('/certificates/<string:option>/<int:cer_id>', methods=['GET', 'POST'])
@login_required
def certificates(option, cer_id):
    page = request.args.get('page', 1, type=int)
    pagination = Certificate.query.order_by(Certificate.id).\
        paginate(page, per_page=current_app.config['CERS_PER_PAGE'], error_out=False)
    cers = pagination.items
    if option == 'add':
        form = CertificateForm()
        if form.validate_on_submit():
            if not Certificate.query.filter_by(name=form.name.data).first():
                new_cer = Certificate(name=form.name.data, username=form.username.data, password=form.password.data)
                db.session.add(new_cer)
                db.session.commit()
                flash('添加凭证成功', 'success')
                return redirect(url_for('main.certificates', page=page))
            flash('该凭证已存在', 'error')
            return redirect(url_for('main.certificates', option='add', page=page))
        return render_template('main/certificates.html', form=form, page=page)
    if option == 'delete' and cer_id:
        if Switch.query.filter_by(cer_id=cer_id).first():
            flash('该凭证已经被使用，无法删除', 'error')
            return redirect(url_for('main.certificates', page=page))
        cer = Certificate.query.get_or_404(cer_id)
        db.session.delete(cer)
        db.session.commit()
        flash('删除凭证成功', 'success')
        return redirect(url_for('main.certificates'))
    if option == 'edit' and cer_id:
        cer = Certificate.query.get_or_404(cer_id)
        form = CertificateForm()
        if form.validate_on_submit():
            verify_cer = Certificate.query.filter_by(name=form.name.data).first()
            if not verify_cer or verify_cer == cer:
                cer.name = form.name.data
                cer.username = form.username.data
                cer.password = form.password.data
                flash('修改凭证成功', 'success')
                return redirect(url_for('main.certificates', page=page))
            flash('该凭证已存在', 'error')
            return redirect(url_for('main.certificates', option='edit', cer_id=cer.id, page=page))
        form.name.data = cer.name
        form.username.data = cer.username
        return render_template('main/certificates.html', form=form, page=page)
    return render_template('main/certificates.html', cers=cers, pagination=pagination, page=page)


# 返回IP检测结果
@main.route('/check_result', methods=['GET', 'POST'])
@login_required
def check_result():
    ip_address = request.args.get('ip_address', '', type=str)
    redis_key = 'check_ip_%s' % ip_address
    if ip_address == '':
        abort(404)
    ip = IPAddress.query.filter_by(ip_address=ip_address).first()
    if not ip:
        abort(404)
    result_list = redis_store.lrange(redis_key, 0, -1)
    result_dic = {}
    for line in ip.lines:
        result_dic[line.name] = []
    for r in result_list:
        rl = r.split(',')
        line = Line.query.get_or_404(int(rl[0]))
        switch = Switch.query.get_or_404(int(rl[1]))
        result_dic[line.name].append((switch.description, int(rl[2]), switch.level))
    for k, v in result_dic.items():
        result_dic[k] = sorted(v, key=lambda x: x[2])
    return jsonify(result_dic)


# 端口扫描
@main.route('/scan_port', methods=['GET', 'POST'])
@login_required
def scan_port():
    ip_address = request.args.get('ip_address', '', type=str)
    form = ScanPortForm()
    if form.validate_on_submit():
        return redirect(url_for('main.scan_port', ip_address=form.ip_address.data))
    form.ip_address.data = ip_address
    if ip_address != '':
        ips = get_ips(ip_address)
        redis_key = 'scan_port_%s' % ip_address
        redis_store.delete(redis_key)
        if not ips:
            flash('请输入正确的IP地址', 'error')
            return redirect(url_for('main.scan_port'))
        for ip in ips:
            portscanner.delay(redis_key, ip)
        flash('IP检测中，请注意查看下方结果', 'success')
    return render_template('main/scan_port.html', form=form)


# 返回端口扫描结果
@main.route('/scan_result', methods=['GET', 'POST'])
@login_required
def scan_result():
    ip_address = request.args.get('ip_address', '', type=str)
    redis_key = 'scan_port_%s' % ip_address
    if ip_address == '':
        abort(404)
    result_list = redis_store.lrange(redis_key, 0, -1)
    result_dic = {}
    for r in result_list:
        host = r.split(':')[0]
        ports = r.split(':')[1]
        result_dic[host] = ports
    return jsonify(result_dic)

