
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
    RepoManager.install("midonet-cluster-mem")
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

    domain_id = run(". admin-openrc ; openstack domain list | grep default | awk '{print $2;}'")

    #
    # mn-conf set -c -t default wipes the mn-conf clean, make sure you do not do it anywhere after here
    # the reason we need it here is to avoid keystone.domain_name being preset
    #
    run("""
mn-conf set -c -t default <<EOF
cluster.auth {
    provider_class = "org.midonet.cluster.auth.keystone.KeystoneService"
    admin_role = "admin"
    keystone.tenant_name = "admin"
    keystone.admin_token = "%s"
    keystone.host = %s
    keystone.port = 35357
    keystone.domain_id = %s
}
EOF
""" % (
        passwords["ADMIN_TOKEN"],
        keystone_ip,
        domain_id))

    run("""
cat >/etc/midonet/midonet.conf<<EOF
[zookeeper]
zookeeper_hosts = %s
EOF

mn-conf set -t default <<EOF
zookeeper {
    zookeeper_hosts = "%s"
}

cassandra {
    servers = "%s"
    cluster = "midonet"
}
EOF

echo "cassandra.replication_factor : %s" | mn-conf set -t default

""" % (
        ",".join(zookeeper_hosts),
        ",".join(zookeeper_hosts),
        ",".join(cassandra_hosts),
        cassandra_count))

    ServiceControl.launch("midonet-cluster", "org.midonet.cluster.ClusterNode")

    run("""
for i in $(seq 1 30); do
    midonet-cli -e 'tunnel-zone list' 1>/dev/null 2>/dev/null && break
    sleep 1
done
""")

    run("""
midonet-cli -e 'tunnel-zone list' | grep 'name vxlan' || midonet-cli -e 'tunnel-zone create name vxlan type vxlan'
""")

    run("""
midonet-cli -e 'tunnel-zone list' | grep 'name gre' || midonet-cli -e 'tunnel-zone create name gre type gre'
""")
