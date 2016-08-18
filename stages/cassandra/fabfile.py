
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
@roles('cassandra')
def cassandra():

    RepoManager.install("openjdk-8-jre-headless")
    RepoManager.install("dsc22")
    RepoManager.install("netcat")

    run("""
systemctl stop cassandra; echo
ps axufwwwwwwwwwwwwwwwwwwwwwwwwww | grep -v grep | grep org.apache.cassandra.service.CassandraDaemon | awk '{print $2;}' | xargs -n1 --no-run-if-empty kill -9

rm -rfv /var/lib/cassandra/*
""")

    run("""
uudecode -o /etc/cassandra/cassandra.yaml.bz2 <<EOF
begin-base64-encoded 644 \
L2V0Yy9jYXNzYW5kcmEvY2Fzc2FuZHJhLnlhbWwuYnoy
QlpoOTFBWSZTWeBWA/8AAkLfgHEQWIf/9S4nXkC/7//wUAXHXdWZryLd3NTD
W2E1CSRqAaEzVT9NERoxDJk00ZM0mgaBkRinpE1AAAA00AAAACREJkRo1U/T
U2pqbMqGj1NAZAyGgBtSpoAAPUAaBoAAAGgAkUapmRMCp+iE9EAAAAAHqLwp
SGTBqHYjqb8bHlo9G2Oltml/lHDz7eKuzBsYlWPdLPvpzuvza7x2QyzrnlDf
IKM8yJQ3ZCFTxiO8NGcYZk0emA8yAsgTk5lcZCLbAJmPrubyUZ0QRfo8I/pg
sqgl0TwXKdcHMx75Zy2ntWip94w014qJSm3rAHhEI6xHZryZDo6NB5tV8oyc
uGlaifnQFyBIo9TmZZrlUABuJd0DCaGCjIQmOS9BCvekQwrG9yje1laFzw1x
X+x3djtV/S4rDBwoiPXIBQEIquyGook5XHw5sYWkS9lWGlUqwpEKmbnG6enk
d/oeoyH8I/U7jpXgy6lwOBVwt8bdOh7YVz1wKaenAd05w8nP3KWyFhs4Ocfm
BPfAm1Y3PzcsuN9vu6+Tm5xoUEXPXlYifbH4zWsfGY6xBhewg1kg0YSq0Zud
RqnHPjFysClywu1RiVd8vhao5a9jV2Foi7omehomhg1Cl7w+LlxTbVji4gUn
DILJDto1ZJBj+qGut8o1rkmUvVtN+GISlUUGy1Ae3zwr4kikywtMQt5zuklO
ledqC0oNebDIyEbgw76zoYrHboDQn52YFLGg7sLicAcF41+lmipU/qkjsTG2
PvVk/FEkVxy3wNtslbqoL+ldy/ZX8rt7juAaDtsQS6Dxmm8MNGNqVEJ2zm0J
p6qIVydNgZ0UoJJcWel+OlVkof8xmaLjWivUysktFeTGtyjPEbZ2DbbXJbQs
pPlqEb5P/XTBSdNX34KlAopcFY2BaYETLF71NzjG0iWFcELFrard1/E8E9Vd
mOXnoELq9GrZsCyAEbWAuxnnMpM0pdceWc7TBAmdmlUpz1nhVTjVI0Zkllp6
jgtAOmixNg60EoLo2Gs3GCaKS6iW0iKUwAoNBe1qMnxHLRKBm66YLPVPVTMi
DYakZasqED7y9IWDMe0qnPaqDfUKOF6M70kzeixyU2t0HiipJlAkjawshO5B
YPellkdZmFypjcOAwrN1tOvFIBj108ZcUOHGociYkW26ZPFu0Zhtmcjcy1co
QXbFJ8NZsYEEFRWo+zG1A4U61uyL4GJtSPKyE7Sos6iloQyiYSsiLH0LvI0l
GeLqMlKuMpAiVLPS1E5+OgXk0OdzNq6gMDGTkQxgSnufny2JDkDz4FEvC3NL
z4lD0VGkYSGs5JJTQ4NvUyEdUxdWtU9xmlIvJjVQloBMxGZHaMVtRh0qhzz4
MLkceoNKI2tfBvqLonLxuM1mq8bYAo0OyymWC4NWiMhydV7p0KtRtttU88k5
SMKlJpKmxXXEKcEbBMlhYEi43lq8d0G9hQLSqKttheBMCSSDNPea6yd5SdhN
qaS5Gzka1xpaobVlyI4Ly4+M9EDnvI5TGWAN5BKUvaYqw0VTXkRAhmViVEpZ
UJx1NCmfQ2Y23ZSXVuktz09AWepwN96pauxV3cECZwOcyy5RjG9HA3BDBsKM
UyiLAMmoGg6NWxzrbDGRK8JwaBCK0qXhYmkVUyEzMHt2zC1WGhS9TMS/EP8B
pXvV1xrVpsqCXLtqXRkqaXsUQNZc2rMUCtOS4EJjIJUS3IxzTkp+604rCpPE
gnxTIeyuQ4RVApJH/F3JFOFCQ4FYD/w=
====
EOF

rm -rfv /etc/cassandra/cassandra.yaml

bzip2 -d /etc/cassandra/cassandra.yaml.bz2
""")

    my_ip = metadata.servers[env.host_string]['ip']

    run("""
sed -i 's,XXX_LISTEN_ADDRESS,%s,g;' /etc/cassandra/cassandra.yaml
sed -i 's,XXX_RPC_ADDRESS,%s,g;' /etc/cassandra/cassandra.yaml

ed -i 's,XXX_CLUSTER_NAME,Midonet,g;' /etc/cassandra/cassandra.yaml
sed -i 's,start_rpc: false,start_rpc: true,g;' /etc/cassandra/cassandra.yaml
sed -i 's,enable_user_defined_functions: false,enable_user_defined_functions: true,g;' /etc/cassandra/cassandra.yaml
""" % (my_ip, my_ip))

    seeds = []

    for server in metadata.roles['cassandra']:
        seeds.append(metadata.servers[server]['ip'])

    run("""
sed -i 's;"XXX_SEEDS_SEEDS_SEEDS";%s;g;' /etc/cassandra/cassandra.yaml
""" % ",".join(seeds))

    ServiceControl.launch("cassandra", "org.apache.cassandra.service.CassandraDaemon")

    run("""
for i in $(seq 1 30); do
    nodetool --host 127.0.0.1 status 2>/dev/null 1>/dev/null && break
    sleep 1
done

nodetool --host 127.0.0.1 status
""")

    for server in metadata.roles['cassandra']:
        run("""
SERVER="%s"

for i in $(seq 1 60); do
    nodetool --host 127.0.0.1 status | grep -- "${SERVER}" && break
    sleep 1
done

nodetool --host 127.0.0.1 status | grep -- "${SERVER}"

""" % metadata.servers[server]['ip'])

