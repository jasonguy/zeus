
import socket

import os
import sys

from zeus.config import ConfigManager

from fabric.api import puts, local
from fabric.colors import yellow

#
# via http://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
#
def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:
        return False

    return True

def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:
        return False
    return True

def pingcheck():
    metadata = ConfigManager(os.environ["CONFIGFILE"])

    domain = metadata.config["domain"]
    for server in sorted(metadata.servers):
        server_ip = metadata.servers[server]["ip"]
        puts(yellow("pinging %s.%s (%s)" % (server, domain, server_ip)))
        if is_valid_ipv4_address(server_ip):
            local("ping -c1 -W20 %s" % server_ip)
        elif is_valid_ipv6_address(server_ip):
            local("ping6 -c1 -W20 %s" % server_ip)
        else:
            sys.exit(1)

