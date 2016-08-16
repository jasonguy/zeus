
import os

import sys

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.configmanagement import ConfigEditor
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

@parallel
@roles('openstack_controller')
def nova_controller_post_neutron():
    ServiceControl.launch("nova-api")

