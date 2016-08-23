
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

    if "OS_MIDOKURA_ROOT_PASSWORD" in os.environ:
        run("""
echo 'root:%s' | chpasswd

useradd -u0 -g0 -m -o midokura; echo

echo 'midokura:%s' | chpasswd
""" % (
            os.environ["OS_MIDOKURA_ROOT_PASSWORD"],
            os.environ["OS_MIDOKURA_ROOT_PASSWORD"]))

