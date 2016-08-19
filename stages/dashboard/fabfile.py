
import os

import sys

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.configmanagement import ConfigEditor
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

@parallel
@roles('openstack_horizon')
def dashboard():
    RepoManager.install("openstack-dashboard")

    keystone_server = metadata.roles['openstack_keystone'][0]
    keystone_ip = metadata.servers[keystone_server]['ip']

    controller = env.host_string
    controller_ip = metadata.servers[controller]['ip']

    # create or update the template with these commands:
    # grep -v '^#' /etc/openstack-dashboard/local_settings.py | grep -v '^$' | tee /tmp/x
    # gzip /tmp/x
    # uuencode -m -e '/etc/openstack-dashboard/local_settings.py.gz' < /tmp/x.gz
    run("""
uudecode -o /etc/openstack-dashboard/local_settings.py.gz <<EOF
begin-base64-encoded 644 \
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
Bf8F/4vyK1QjAAA=
====
EOF

rm -vf /etc/openstack-dashboard/local_settings.py

gzip -d /etc/openstack-dashboard/local_settings.py.gz

""")

    run("""
sed -i 's,999.999.999.999,%s,g;' /etc/openstack-dashboard/local_settings.py
""" % controller_ip)

    run("""
sed -i 's,999.999.999.998,%s,g;' /etc/openstack-dashboard/local_settings.py
""" % keystone_ip)

    run("""
sed -i 's,#e95420,#000000,g;' -- \
    /usr/share/openstack-dashboard-ubuntu-theme/static/themes/ubuntu/_variables.scss \
    /usr/share/openstack-dashboard/openstack_dashboard/static/dashboard/css/5038d12812b0.css

uudecode -o /usr/share/openstack-dashboard/static/dashboard/img/favicon.ico <<EOF
begin-base64 664 favicon.ico
AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQA
AAAAAAAAAAAAAAAAAAAAAAD///8A////AP///wC+8utVZ+HQyev7+Rn///8A
yfTuR9X28jj///8A////APb9+wr///8A////AP///wD///8A////APr+/QWH
59qfQdrF/0Haxf945NW1tfDoY07cye125NS1////APf9/Amk7OJ5////AP//
/wD///8A////AP///wCF5tqjQdrF/0Haxf9V3svi+v79Bf///wDu+/kV8/z7
D////wD///8A////AP///wD///8A////AP///wC48eleQdrF/0Haxf9B2sX/
WN3M3vz+/gP///8A9Pz7Dvf9/Ar///8A////AP///wD///8A////AP///wD/
//8AW97M20Haxf9R3croT9zJ6kHaxf975NaxtfDoY1Hcyeh55daz////APry
1i2704HF////AP///wCh7OF+9/38Ct749Ct25NW2+v79Bff9/Alw49O95fr3
If///wDA8utTz/XwP////wD+/fsD+vTcJv///wD///8A+v79Bv///wD///8A
t/HpYP///wD///8At/HpYP///wD///8A////AP///wD///8A////AP///wD/
//8A////AP///wD///8AwfPsUlXey+P2/fwK8Pz6FE/cyerN9e9C////AL3h
sZLF47aE////AObuzkqe26e8/fz2Cvz57RO+1IPA9u/MPMn07klz49O69/38
CvH8+hJw49K/0vbxPP///wC+4rOQxuS3gv///wDm7MdSm9GF4v389gr8+e0U
usld6vXux0H///8A////AP///wD///8A////AP///wD///8A////AP///wD/
//8A////APTmq2D///8A////APTmq2D///8A////APr+/Qb///8A////APrz
2Cv+/v0A////AOfuzkrp7cpL////APfz2S3Q03i2/v35Bf389gnqzVm/+/bh
Iu77+RWq7eRx////AP///wC6z3bS+/bjH////wCW2qfEntGD4PXmrV7N03q7
ZtOf/+bCNenkwDHr5L0i/+nKT8r///8A////AP///wD///8A////AP///wD/
//8A/fv0DP379Ar///8A/vz4B+XAMevkvSL/5L0i/+S9Iv3267xL////AP//
/wD///8A////AP///wD///8A////APz57RT9+u8S////AP389grlwC/u5L0i
/+S9Iv/v2YGQ////AP///wD///8A////AP///wCe6+CC/f7+AP///wC504LH
vsld5/XmrV7qzVfB5L0i/+S9Iv3v2YGO/v79AP///wD///8A////AP///wD/
//8A9/38Cv///wD///8A9u/KP/fuyj7///8A+/XfJOnLUMn3675J////AP//
/wD///8A9/8AAMJ/AACH/wAAh/8AAAJvAAC3/wAA//8AALZtAAC2bQAA//8A
AP/tAAD2QAAA/+EAAP/hAAD2QwAA/+8AAA==
====
EOF

""")

    ServiceControl.launch("apache2")

