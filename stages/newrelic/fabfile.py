
import os
import sys

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

FabricManager.setup(metadata.roles)

@parallel
@roles('all_servers')
def newrelic():
    if "NEWRELIC_LICENSE_KEY" not in os.environ:
        sys.exit(0)

    run("""
mkdir -pv /etc/apt/sources.list.d
cat >/etc/apt/sources.list.d/newrelic.list<<EOF
deb [arch=amd64] http://apt.newrelic.com/debian/ newrelic non-free
EOF
""")

    RepoManager.repokey("https://download.newrelic.com/548C16BF.gpg")

    run("""
rm -fv /etc/newrelic/nrsysmond.cfg* || true
""")

    RepoManager.install("newrelic-sysmond")

    run("""

SERVER_NAME="%s"
DOMAIN_NAME="%s"
LICENSE_KEY="%s"

cat>/etc/newrelic/nrsysmond.cfg<<EOF
license_key=${LICENSE_KEY}
loglevel=info
logfile=/var/log/newrelic/nrsysmond.log
hostname=${SERVER_NAME}.${DOMAIN_NAME}
EOF

nrsysmond-config --set license_key="${LICENSE_KEY}"
""" % (
        env.host_string,
        metadata.config["domain"],
        os.environ["NEWRELIC_LICENSE_KEY"]))

    ServiceControl.launch("newrelic-sysmond", "nrsysmond")

