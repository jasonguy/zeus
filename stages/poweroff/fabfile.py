
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel, roles, run

metadata = ConfigManager(os.environ["CONFIGFILE"])

FabricManager.setup(metadata.roles)


@parallel
@roles('all_servers')
def poweroff():

    run("""
poweroff; echo
""")

