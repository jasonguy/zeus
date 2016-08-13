
import os
from zeus.config import ConfigManager

from fabric.api import puts,local
from fabric.colors import yellow

metadata = ConfigManager(os.environ["CONFIGFILE"])

def pingcheck():
    domain = metadata.config["domain"]
    for server in sorted(metadata.servers):
        ip = metadata.servers[server]["ip"]
        puts(yellow("pinging %s.%s (%s)" % (server,domain,ip)))
        local("ping -c1 -W20 %s" % ip)

