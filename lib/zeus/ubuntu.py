
from fabric.api import run

class RepoManager(object):
    def __init__(self):
        return

    @classmethod
    def repokey(cls, url):
        run("""
URL="%s"

wget -SO- "${URL}" | apt-key add -
""" % url)

    @classmethod
    def install(cls, package_name):
        run("""
PACKAGE_NAME="%s"

export DEBIAN_FRONTEND=noninteractive

yes | dpkg --configure -a
apt-get -y -u --force-yes install

apt-get -y -u install "${PACKAGE_NAME}"

apt-get clean

apt-get -y autoremove

""" % package_name)

    @classmethod
    def remove(cls, package_name):
        run("""
PACKAGE_NAME="%s"

export DEBIAN_FRONTEND=noninteractive

apt-get -y -u purge "${PACKAGE_NAME}"

yes | dpkg --configure -a
apt-get -y -u --force-yes install

apt-get clean

apt-get -y autoremove

""" % package_name)

