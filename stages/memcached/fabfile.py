
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel, roles, run

metadata = ConfigManager(os.environ["CONFIGFILE"])

FabricManager.setup(metadata.roles)


@parallel
@roles('openstack_controller')
def memcached():

    RepoManager.install("memcached")
    RepoManager.install("python-memcache")

    controller = metadata.roles['openstack_controller'][0]
    controller_ip = metadata.servers[controller]['ip']

    run("""
cat >/etc/memcached.conf <<EOF
-d
logfile /var/log/memcached.log
-m 64
-p 11211
-u memcache
-l %s
EOF
""" % controller_ip)

    ServiceControl.launch("memcached")

