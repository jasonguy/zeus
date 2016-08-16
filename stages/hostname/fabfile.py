
import os
import sys

from zeus.config import ConfigManager
from zeus.common import FabricManager

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

FabricManager.setup(metadata.roles)

@parallel
@roles('all_servers')
def hostname():
    hosts = []

    for server in sorted(metadata.servers):
        hosts.append("%s %s.%s %s" % (
            metadata.servers[server]["ip"],
            server,
            metadata.config['domain'],
            server))

    run("""
HOSTNAME="%s"
DOMAIN="%s"

echo "${HOSTNAME}" >/etc/hostname

hostname "${HOSTNAME}"

cat >/etc/hosts<<EOF
127.0.0.1   localhost.localdomain localhost

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

%s

EOF

if [[ ! "$(hostname)" == "${HOSTNAME}" ]]; then
    exit 1
fi

if [[ ! "$(hostname -f)" == "${HOSTNAME}.${DOMAIN}" ]]; then
    exit 1
fi

""" % (
        env.host_string,
        metadata.config['domain'],
        "\n".join(hosts)))

    sys.exit(0)

