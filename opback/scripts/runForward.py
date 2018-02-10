# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
from forward.api import Forward
from tempfile import NamedTemporaryFile
script_text = u"""# -*- coding:utf-8 -*-
def node(nodeInput):
    # init njInfo
    njInfo = {
        'status':True,
        'errLog':'',
        'content':{}
    }

    # node
    for device in nodeInput['instance']:
        instance = nodeInput['instance'][device]
        version = instance.execute('cat /etc/redhat-release')
        njInfo['params'] = nodeInput['parameters']
        if version['status']:
            # execute succeed
            njInfo['content'][device] = version['content']
        else:
            njInfo['status'] = False
            njInfo['errLog'] = '%s%s:%s\\r\\n' % (
                njInfo['errLog'], device, version['errLog'])
    njInfo['chinese'] = '你好'
    return njInfo
"""
script_file = NamedTemporaryFile(delete=False)
script_file.write("""%s""" % script_text.encode('utf-8'))
script_file.close()
args = 'hello world'
print script_file.name

inventory = [
    dict(ip='127.0.0.1', vender='bclinux7', model='bclinux7',
         connect='ssh', conpass='111111', actpass='',
         remote_port=22, remote_user='maiyifan',),
    dict(ip='192.168.182.14', vender='bclinux7', model='bclinux7',
         connect='ssh', conpass='111111', actpass='',
         remote_port=22, remote_user='maiyifan',),
    dict(ip='192.168.182.16', vender='bclinux7', model='bclinux7',
         connect='ssh', conpass='111111', actpass='',
         remote_port=22, remote_user='maiyifan',)]
forward = Forward(
    worker=4, script=script_file.name, args=args,
    loglevel='info', logfile='.log/forward.log',
    no_std_log=True, out='stdout',
    inventory=inventory, timeout=2)
result = forward.run()
print "here is result:"
print result
