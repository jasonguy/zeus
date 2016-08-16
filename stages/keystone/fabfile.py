
import os

import sys

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel,roles,run,env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

@parallel
@roles('openstack_keystone')
def keystone():

    run("""
echo "manual" > /etc/init/keystone.override
""")

    RepoManager.install("keystone")
    RepoManager.install("apache2")
    RepoManager.install("libapache2-mod-wsgi")

    run("""
XKV="/usr/share/zeus/bin/xkv.py set /etc/keystone/keystone.conf"

${XKV} DEFAULT admin_token %s
""" % passwords["ADMIN_TOKEN"])

