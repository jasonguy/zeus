
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

@parallel
@roles('zookeeper')
def zookeeper():

    RepoManager.install("openjdk-8-jre-headless")
    RepoManager.install("zookeeper")
    RepoManager.install("zookeeperd")
    RepoManager.install("zkdump")
    RepoManager.install("netcat")

    run("""
cat >/etc/zookeeper/conf/zoo.cfg<<EOF
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/var/lib/zookeeper
clientPort=2181
autopurge.snapRetainCount=10
autopurge.purgeInterval=12
EOF
""")

    zkid = 0
    #
    # this is fun.
    #
    for zkserver in sorted(metadata.roles["zookeeper"]):
        zkid = zkid + 1
        run("""
cat >>/etc/zookeeper/conf/zoo.cfg<<EOF
server.%s=%s:2888:3888
EOF
""" % (
            zkid,
            metadata.servers[zkserver]['ip']))

        if zkserver == env.host_string:
            run("""
echo "%s" >/etc/zookeeper/conf/myid
""" % zkid)

    ServiceControl.launch("zookeeper")

    run("""
for i in $(seq 1 10); do
    echo ruok | nc localhost 2181 | grep imok && break || sleep 1
done

echo ruok | nc localhost 2181 | grep imok
""")

    run("""
echo stat | nc localhost 2181
""")

