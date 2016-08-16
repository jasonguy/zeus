
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.ubuntu import RepoManager

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

@parallel
@roles('openstack_rabbitmq')
def rabbit():

    RepoManager.install("rabbitmq-server")

    run("""
rabbitmqctl change_password openstack "%s" || \
    rabbitmqctl add_user openstack "%s"

""" % (passwords["RABBIT_PASS"], passwords["RABBIT_PASS"]))

    run("""
rabbitmqctl set_permissions openstack ".*" ".*" ".*"
""")

