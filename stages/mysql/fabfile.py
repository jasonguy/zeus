
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
@roles('openstack_mysql')
def mysql():

    RepoManager.install("mariadb-server")
    RepoManager.install("python-pymysql")

    run("""
IP="%s"

cat >/etc/mysql/mariadb.conf.d/51-openstack.cnf <<EOF
[mysqld]
bind-address = ${IP}

default-storage-engine = innodb
innodb_file_per_table
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8
EOF

""" % metadata.servers[env.host_string]["ip"])

    ServiceControl.launch("mysql", "mysqld")

    for database in ["keystone", "glance", "nova_api", "nova", "neutron"]:
        run("""
echo 'create database if not exists %s;' | mysql -uroot
""" % database)

        run("""
cat <<EOF | mysql -uroot
GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' IDENTIFIED BY '%s';
EOF
""" % (database, database, passwords["%s_DBPASS" % database.upper()]))

        run("""
cat <<EOF | mysql -uroot
GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' IDENTIFIED BY '%s';
EOF
""" % (database, database, passwords["%s_DBPASS" % database.upper()]))

