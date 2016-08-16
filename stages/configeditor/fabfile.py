
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.ubuntu import RepoManager

from fabric.api import parallel, roles, run

FabricManager.setup(ConfigManager(os.environ["CONFIGFILE"]).roles)

@parallel
@roles('all_servers')
def configeditor():
    RepoManager.install("sharutils")

    run("""

mkdir -pv /usr/share/zeus/bin

touch /usr/share/zeus/bin/xkv.py
chmod 0755 /usr/share/zeus/bin/xkv.py

cat >/usr/share/zeus/bin/xkv.py <<EOF
#!/usr/bin/env python

import sys
import ConfigParser

def add_section(configuration, section):
    if not(section == 'DEFAULT' or configuration.has_section(section)):
        configuration.add_section(section)

def set_option(configfile, configuration, section, option, value):
    configuration.set(section, option, value)

    cfgfile = open(configfile, "w")
    configuration.write(cfgfile)
    cfgfile.close()

def get_option(configuration, section, option):
    print configuration.get(section, option)

def handle_command(args):
    command = args[1]
    configfile = args[2]
    section = args[3]
    option = args[4]

    configuration = ConfigParser.RawConfigParser()
    configuration.read(configfile)

    if command == 'set':
        value = args[5]
        add_section(configuration, section)
        set_option(configfile, configuration, section, option, value)

    if command == 'get':
        get_option(configuration, section, option)

    return 0

if __name__ == "__main__":
    sys.exit(handle_command(sys.argv))

EOF

""")


