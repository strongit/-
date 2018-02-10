# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
import sys
sys.path.append('.')

from promise.ansiAdapter.ansiAdapter import ShellExecAdapter
from promise import app

# import ansiAdapter
# You may want this to run as user root instead
# or make this an environmental variable, or
# a CLI prompt. Whatever you want!
# become_user_password = 'foo-whatever'

run_data = {
    'walker_id': 'bar',
    'user_id': '123123'
}

hostnames = ['192.168.182.1', '192.168.182.12']
# hostnames = ['127.0.0.1']
# private_key_file = ROOT_SSH_KEY_FILE
private_key_file = app.config['ADMIN_SSH_KEY_FILE']
shell = "date>run_result;sleep 3;date>>run_result;cat run_result;"
# shell = "dfkdjf"
become_pass = None
# remote_user = 'root'
remote_user = 'admin'
print private_key_file

shellExecAdapter = ShellExecAdapter(
    hostnames, remote_user, private_key_file, run_data, become_pass, shell)
[result, stats_sum, hostvars] = shellExecAdapter.run()
print result
print stats_sum
print hostvars
