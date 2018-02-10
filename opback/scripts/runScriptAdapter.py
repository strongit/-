# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
import sys
sys.path.append('.')

from promise.ansiAdapter.ansiAdapter import ScriptExecAdapter
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
private_key_file = app.config['ADMIN_SSH_KEY_FILE']
script = """#!/usr/bin/python
#-*- coding:utf-8 -*-
import os
print os.path.dirname('/tmp/')
    """
become_pass = None
remote_user = 'admin'
params = 'params1 params2'

scriptExecAdapter = ScriptExecAdapter(
    hostnames, remote_user, private_key_file, run_data, become_pass, script,
    params)
[result, stats_sum, hostvars] = scriptExecAdapter.run()
print result
print stats_sum
print hostvars
