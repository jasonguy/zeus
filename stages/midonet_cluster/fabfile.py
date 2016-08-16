
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

@parallel
@roles('midonet_cluster')
def midonet_cluster():

    RepoManager.install("midonet-cluster")
    RepoManager.install("netcat")

    keystone_server = metadata.roles['openstack_keystone'][0]
    keystone_ip = metadata.servers[keystone_server]['ip']

    zookeeper_hosts = []
    for zkserver in sorted(metadata.roles["zookeeper"]):
        zookeeper_hosts.append("%s:2181" % metadata.servers[zkserver]['ip'])

    cassandra_count = 0
    cassandra_hosts = []
    for ckserver in sorted(metadata.roles["cassandra"]):
        cassandra_count = cassandra_count + 1
        cassandra_hosts.append(metadata.servers[ckserver]['ip'])

    run("""
cat >/etc/midonet/midonet.conf<<EOF
[zookeeper]
zookeeper_hosts = %s
EOF

cat << EOF | mn-conf set -t default
zookeeper {
    zookeeper_hosts = "%s"
}

cassandra {
    servers = "%s"
}
EOF

echo "cassandra.replication_factor : %s" | mn-conf set -t default

$ cat << EOF | mn-conf set -t default
cluster.auth {
    provider_class = "org.midonet.cluster.auth.keystone.KeystoneService"
    admin_role = "admin"
    keystone.tenant_name = "admin"
    keystone.admin_token = "%s"
    keystone.host = %s
    keystone.port = 35357
}
EOF
""" % (
        ",".join(zookeeper_hosts),
        ",".join(zookeeper_hosts),
        ",".join(cassandra_hosts),
        cassandra_count,
        passwords["ADMIN_TOKEN"],
        keystone_ip))

    ServiceControl.launch("midonet-cluster")

