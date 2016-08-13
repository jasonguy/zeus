
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel,roles,run

metadata = ConfigManager(os.environ["CONFIGFILE"])

FabricManager.setup(metadata.roles)

@parallel
@roles('all_servers')
def cloudarchive():
    RepoManager.install("software-properties-common")

    run("""
# TRUSTY add-apt-repository cloud-archive:mitaka
""")

    RepoManager.install("python-openstackclient")

