
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager

from fabric.api import parallel, roles, run

FabricManager.setup(ConfigManager(os.environ["CONFIGFILE"]).roles)

@parallel
@roles('all_servers')
def connectcheck():
    run("""
lsb_release -a | grep ^Codename | grep xenial
""")

