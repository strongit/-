# -*- coding:utf-8 -*-
from app import celery, redis_store
import sys
import paramiko
import masscan

reload(sys)
sys.setdefaultencoding('utf8')


@celery.task()
def remote_ping(ip_address, switch_ip, username, password, line_id, swtich_id):
    redis_key = 'check_ip_%s' % ip_address
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=switch_ip, username=username, password=password, port=22, auth_timeout=5, timeout=5)
        cmd = 'ping -a %s -m 1 -c 2 %s' % (switch_ip, ip_address)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        if "100.00% packet loss" in stdout.read():
            ssh.close()
            redis_store.rpush(redis_key, "%s,%s,0" % (line_id, swtich_id))
            return False
        ssh.close()
        redis_store.rpush(redis_key, "%s,%s,1" % (line_id, swtich_id))
        return True
    except Exception, e:
        redis_store.rpush(redis_key, "%s,%s,2" % (line_id, swtich_id))
        return False


@celery.task
def portscanner(redis_key, host):
    try:
        mas = masscan.PortScanner()
        mas.scan(host, ports='0-65535', arguments='--rate=10000')
        ports_list = mas.scan_result['scan'][host]['tcp'].keys()
        ports = ','.join(map(str, ports_list))
        redis_store.rpush(redis_key, '%s:%s' % (host, ports))
        return True
    except Exception, e:
        redis_store.rpush(redis_key, '%s:%s' % (host, '获取端口失败，请检查该主机状态'))
        return False
