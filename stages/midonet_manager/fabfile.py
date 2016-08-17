
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
@roles('midonet_manager')
def midonet_manager():

    RepoManager.install("midonet-manager")

    midonet_server = metadata.roles['midonet_cluster'][0]
    cluster_ip = metadata.servers[midonet_server]['ip']

    analytics_server = metadata.roles['midonet_analytics'][0]
    analytics_ip = metadata.servers[analytics_server]['ip']

    run("""
CLUSTER_IP="%s"
INSIGHT_IP="%s"

cat >/var/www/html/midonet-manager/config/client.js<<EOF
{
  "api_host": "http://${CLUSTER_IP}:8181",
  "login_host": "http://${CLUSTER_IP}:8181",
  "trace_api_host": "http://${CLUSTER_IP}:8181",
  "traces_ws_url": "ws://${CLUSTER_IP}:8460/trace",
  "api_namespace": "midonet-api",
  "api_version": "5.0",
  "api_token": false,
  "agent_config_api_namespace": "conf",
  "analytics_ws_api_url": "ws://${INSIGHT_IP}:8080/analytics",
  "poll_enabled": true,
  "login_animation_enabled": false
}
EOF

""" % (
        cluster_ip,
        analytics_ip))

    ServiceControl.launch("apache2")

