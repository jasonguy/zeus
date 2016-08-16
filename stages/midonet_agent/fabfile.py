
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
@roles('midonet_gateway', 'openstack_compute')
def midonet_agent():

    RepoManager.install("openjdk-8-jre-headless")
    RepoManager.install("midolman")
    RepoManager.install("midonet-jmxscraper")

    openstack_controller = metadata.roles['openstack_controller'][0]
    controller_ip = metadata.servers[openstack_controller]['ip']

    zookeeper_hosts = []
    for zkserver in sorted(metadata.roles["zookeeper"]):
        zookeeper_hosts.append("%s:2181" % metadata.servers[zkserver]['ip'])

    cassandra_count = 0
    cassandra_hosts = []
    for ckserver in sorted(metadata.roles["cassandra"]):
        cassandra_count = cassandra_count + 1
        cassandra_hosts.append(metadata.servers[ckserver]['ip'])

    run("""
cat >/etc/midolman/midolman.conf<<EOF
[zookeeper]
zookeeper_hosts = %s
EOF

mn-conf template-set -h local -t agent-compute-medium

cp -avpx /etc/midolman/midolman-env.sh.compute.medium \
    /etc/midolman/midolman-env.sh

echo 'agent.openstack.metadata.nova_metadata_url : "http://%s:8775"' | mn-conf set -t default
echo 'agent.openstack.metadata.shared_secret : "%s"' | mn-conf set -t default
echo 'agent.openstack.metadata.enabled : true' | mn-conf set -t default

""" % (
        ",".join(zookeeper_hosts),
        controller_ip,
        passwords["NEUTRON_METADATA_SHARED_SECRET"]))

    ServiceControl.launch("midolman")

    run("""
for i in $(seq 1 30); do
    midonet-cli -e 'host list name %s' | grep 'alive true' && break
    sleep 2
done

HOST_UID="$(midonet-cli -e 'host list name %s' | awk '{print $2;}')"

midonet-cli -e "tunnel-zone name vxlan member list" | grep "host ${HOST_UID}" || midonet-cli -e "tunnel-zone name vxlan add member host ${HOST_UID} address %s"

""" % (
        env.host_string,
        env.host_string,
        metadata.servers[env.host_string]['ip']))

