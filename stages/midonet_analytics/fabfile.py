
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
@roles('midonet_analytics')
def midonet_analytics():

    run("""
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/logstash/1.5/debian stable main" >/etc/apt/sources.list.d/logstash.list

wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" >/etc/apt/sources.list.d/elasticsearch.list

apt-get update
""")

    RepoManager.install("logstash")
    RepoManager.install("elasticsearch")
    RepoManager.install("python-pip")

    run("""
pip install -U elasticsearch-curator==3.5
""")

    run("""
systemctl daemon-reload
systemctl enable logstash.service
systemctl enable elasticsearch.service
systemctl daemon-reload
""")

    RepoManager.install("midonet-tools")
    RepoManager.install("midonet-analytics")

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

    analytics_ip = metadata.servers[env.host_string]['ip']

    run("""
cat >/root/analytics_settings.conf<<EOF
clio.enabled : true
clio.service.udp_port : 5001
clio.service.encoding : "binary"
clio.target.udp_endpoint : "%s:5000"
clio.data.fields : [ "cookie", "devices", "host_uuid", "in_port", "in_tenant", "out_ports", "out_tenant", "match_eth_src", "match_eth_dst", "match_ethertype", "match_network_dst", "match_network_src", "match_network_proto", "match_src_port", "match_dst_port", "action_drop", "action_arp_sip", "action_arp_tip", "action_arp_op", "rules", "sim_result", "final_eth_src", "final_eth_dst", "final_net_src", "final_net_dst", "final_transport_src", "final_transport_dst", "timestamp", "type" ]
calliope.enabled : true
calliope.service.ws_port : 8080
calliope.auth.ssl.enabled : false
jmxscraper.enabled : true
jmxscraper.target.udp_endpoint : "%s:5000"
mem_cluster.flow_tracing.enabled : true
mem_cluster.flow_tracing.service.ws_port : 8460
mem_cluster.flow_tracing.auth.ssl.enabled : false
agent.flow_history.enabled : true
agent.flow_history.encoding : "binary"
agent.flow_history.udp_endpoint : "%s:5001"
EOF

mn-conf set -t default </root/analytics_settings.conf

""" % (
        analytics_ip,
        analytics_ip,
        analytics_ip))

    ServiceControl.launch("logstash")
    ServiceControl.launch("elasticsearch")
    ServiceControl.launch("midonet-analytics", "org.midonet.mem.analytics.calliope.CalliopeApp")

