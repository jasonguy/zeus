
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.ubuntu import RepoManager

from fabric.api import parallel, roles

FabricManager.setup(ConfigManager(os.environ["CONFIGFILE"]).roles)

@parallel
@roles('all_servers')
def configeditor():
    RepoManager.install("sharutils")
    RepoManager.install("crudini")

