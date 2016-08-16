
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager

from fabric.api import parallel, roles, puts, run
from fabric.colors import yellow

FabricManager.setup(ConfigManager(os.environ["CONFIGFILE"]).roles)

@parallel
@roles('all_servers')
def distupgrade():
    puts(yellow("updating repositories, this may take a long time."))

    run("""
#
# Round 1: try to apt-get update without purging the cache
#
apt-get update 1>/dev/null

#
# Round 2: clean cache and update again
#
if [[ ! "${?}" == "0" ]]; then
    rm -rf /var/lib/apt/lists/*
    rm -f /etc/apt/apt.conf
    sync
    apt-get update 2>&1
fi
""")

    run("""
export DEBIAN_FRONTEND=noninteractive

debconf-set-selections <<EOF
grub grub/update_grub_changeprompt_threeway select install_new
grub-legacy-ec2 grub/update_grub_changeprompt_threeway select install_new
EOF

yes | dpkg --configure -a
apt-get -y -u --force-yes install
apt-get -y -u --force-yes dist-upgrade 1>/dev/null
""")

    run("""
export DEBIAN_FRONTEND=noninteractive
apt-get -y autoremove
""")

