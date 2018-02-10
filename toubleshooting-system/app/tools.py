# -*- coding:utf-8 -*-
from IPy import IP
import re


def get_ips(ips):
    if re.match(r'^((25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}|(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\/(\d|[1-2]\d|3[0-2]))$', ips):
        try:
            ips = IP(ips)
            return [ip.strNormal(0) for ip in ips]
        except:
            return False
    elif re.match(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}-(25[0-5]|2[0-4]\d|[0-1]?\d?\d)$', ips):
        ipsplit = ips.split('-')
        endip = ipsplit[1]
        iplist = ipsplit[0].split('.')
        preip = '.'.join(iplist[0:3])
        startip = iplist[3]
        if int(endip) <= int(startip):
            return False
        return [preip + '.%s' % ip for ip in range(int(startip), int(endip)+1)]
