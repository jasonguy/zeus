
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.ubuntu import RepoManager

from fabric.api import parallel, roles, run

metadata = ConfigManager(os.environ["CONFIGFILE"])
passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

@parallel
@roles('all_servers')
def cloudarchive():
    RepoManager.install("software-properties-common")
    RepoManager.install("htop")
    RepoManager.install("atop")

    run("""
OS_MIDOKURA_REPOSITORY_USER="%s"
OS_MIDOKURA_REPOSITORY_PASS="%s"

cat >/etc/apt/sources.list.d/datastax.list<<EOF
# DataStax (Apache Cassandra)
deb http://debian.datastax.com/community 2.2 main
EOF

curl -L https://debian.datastax.com/debian/repo_key | apt-key add -

cat >/etc/apt/sources.list.d/midokura.list<<EOF
# MEM
deb http://${OS_MIDOKURA_REPOSITORY_USER}:${OS_MIDOKURA_REPOSITORY_PASS}@repo.midokura.com/mem-5 stable main

# MEM OpenStack Integration
deb http://repo.midokura.com/openstack-mitaka stable main

# MEM 3rd Party Tools and Libraries
deb http://repo.midokura.com/misc stable main
EOF

curl -L https://repo.midokura.com/midorepo.key | apt-key add -

apt-get update

""" % (
        os.environ["OS_MIDOKURA_REPOSITORY_USER"],
        os.environ["OS_MIDOKURA_REPOSITORY_PASS"]))

    RepoManager.install("python-openstackclient")

    run("""
KEYSTONE="%s"
ADMIN_PASS="%s"
DEMO_PASS="%s"
cat >/root/admin-openrc<<EOF
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=$ADMIN_PASS
export OS_AUTH_URL=http://$KEYSTONE:35357/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF

cat >/root/demo-openrc<<EOF
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=demo
export OS_USERNAME=demo
export OS_PASSWORD=$DEMO_PASS
export OS_AUTH_URL=http://$KEYSTONE:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF

""" % (
        metadata.servers[metadata.roles['openstack_keystone'][0]]['ip'],
        passwords["ADMIN_PASS"],
        passwords["DEMO_PASS"]))

