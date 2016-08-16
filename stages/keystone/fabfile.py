
import os

import sys

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager
from zeus.configmanagement import ConfigEditor
from zeus.ubuntu import RepoManager
from zeus.services import ServiceControl

from fabric.api import parallel,roles,run,env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

#
# http://docs.openstack.org/mitaka/install-guide-ubuntu/keystone-install.html
#
@parallel
@roles('openstack_keystone')
def keystone():

    run("""
echo "manual" > /etc/init/keystone.override
""")

    RepoManager.install("keystone")

    run("""
systemctl stop keystone
""")

    RepoManager.install("apache2")
    RepoManager.install("libapache2-mod-wsgi")

    ConfigEditor.setKey("/etc/keystone/keystone.conf", "DEFAULT", "admin_token", passwords["ADMIN_TOKEN"])

    ConfigEditor.setKey(
        "/etc/keystone/keystone.conf",
        "database",
        "connection",
        "mysql+pymysql://keystone:%s@%s/keystone" % (
            passwords["KEYSTONE_DBPASS"],
            metadata.servers[metadata.roles['openstack_mysql'][0]]['ip']))

    ConfigEditor.setKey("/etc/keystone/keystone.conf", "token", "provider", "fernet")

    run("""
su -s /bin/sh -c "keystone-manage db_sync" keystone
""")

    run("""
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
""")

    run("""
uudecode -o /etc/apache2/apache2.conf <<EOF
begin-base64-encoded 644 YXBhY2hlMi5jb25m
U2VydmVyTmFtZSBYWFhYWFhYWFgKTXV0ZXggZmlsZToke0FQQUNIRV9MT0NL
X0RJUn0gZGVmYXVsdApQaWRGaWxlICR7QVBBQ0hFX1BJRF9GSUxFfQpUaW1l
b3V0IDMwMApLZWVwQWxpdmUgT24KTWF4S2VlcEFsaXZlUmVxdWVzdHMgMTAw
CktlZXBBbGl2ZVRpbWVvdXQgNQpVc2VyICR7QVBBQ0hFX1JVTl9VU0VSfQpH
cm91cCAke0FQQUNIRV9SVU5fR1JPVVB9Ckhvc3RuYW1lTG9va3VwcyBPZmYK
RXJyb3JMb2cgJHtBUEFDSEVfTE9HX0RJUn0vZXJyb3IubG9nCkxvZ0xldmVs
IHdhcm4KSW5jbHVkZU9wdGlvbmFsIG1vZHMtZW5hYmxlZC8qLmxvYWQKSW5j
bHVkZU9wdGlvbmFsIG1vZHMtZW5hYmxlZC8qLmNvbmYKSW5jbHVkZSBwb3J0
cy5jb25mCjxEaXJlY3RvcnkgLz4KCU9wdGlvbnMgRm9sbG93U3ltTGlua3MK
CUFsbG93T3ZlcnJpZGUgTm9uZQoJUmVxdWlyZSBhbGwgZGVuaWVkCjwvRGly
ZWN0b3J5Pgo8RGlyZWN0b3J5IC91c3Ivc2hhcmU+CglBbGxvd092ZXJyaWRl
IE5vbmUKCVJlcXVpcmUgYWxsIGdyYW50ZWQKPC9EaXJlY3Rvcnk+CjxEaXJl
Y3RvcnkgL3Zhci93d3cvPgoJT3B0aW9ucyBJbmRleGVzIEZvbGxvd1N5bUxp
bmtzCglBbGxvd092ZXJyaWRlIE5vbmUKCVJlcXVpcmUgYWxsIGdyYW50ZWQK
PC9EaXJlY3Rvcnk+CkFjY2Vzc0ZpbGVOYW1lIC5odGFjY2Vzcwo8RmlsZXNN
YXRjaCAiXlwuaHQiPgoJUmVxdWlyZSBhbGwgZGVuaWVkCjwvRmlsZXNNYXRj
aD4KTG9nRm9ybWF0ICIldjolcCAlaCAlbCAldSAldCBcIiVyXCIgJT5zICVP
IFwiJXtSZWZlcmVyfWlcIiBcIiV7VXNlci1BZ2VudH1pXCIiIHZob3N0X2Nv
bWJpbmVkCkxvZ0Zvcm1hdCAiJWggJWwgJXUgJXQgXCIlclwiICU+cyAlTyBc
IiV7UmVmZXJlcn1pXCIgXCIle1VzZXItQWdlbnR9aVwiIiBjb21iaW5lZApM
b2dGb3JtYXQgIiVoICVsICV1ICV0IFwiJXJcIiAlPnMgJU8iIGNvbW1vbgpM
b2dGb3JtYXQgIiV7UmVmZXJlcn1pIC0+ICVVIiByZWZlcmVyCkxvZ0Zvcm1h
dCAiJXtVc2VyLWFnZW50fWkiIGFnZW50CkluY2x1ZGVPcHRpb25hbCBjb25m
LWVuYWJsZWQvKi5jb25mCkluY2x1ZGVPcHRpb25hbCBzaXRlcy1lbmFibGVk
LyouY29uZgo=
====
EOF
""")

    run("""
sed -i 's,XXXXXXXXX,%s,g;' /etc/apache2/apache2.conf
""" % env.host_string)

    run("""
uudecode -o /etc/apache2/sites-available/wsgi-keystone.conf<<EOF
begin-base64-encoded 644 d3NnaS1rZXlzdG9uZS5jb25m
Ckxpc3RlbiA1MDAwCkxpc3RlbiAzNTM1NwoKPFZpcnR1YWxIb3N0ICo6NTAw
MD4KICAgIFdTR0lEYWVtb25Qcm9jZXNzIGtleXN0b25lLXB1YmxpYyBwcm9j
ZXNzZXM9NSB0aHJlYWRzPTEgdXNlcj1rZXlzdG9uZSBncm91cD1rZXlzdG9u
ZSBkaXNwbGF5LW5hbWU9JXtHUk9VUH0KICAgIFdTR0lQcm9jZXNzR3JvdXAg
a2V5c3RvbmUtcHVibGljCiAgICBXU0dJU2NyaXB0QWxpYXMgLyAvdXNyL2Jp
bi9rZXlzdG9uZS13c2dpLXB1YmxpYwogICAgV1NHSUFwcGxpY2F0aW9uR3Jv
dXAgJXtHTE9CQUx9CiAgICBXU0dJUGFzc0F1dGhvcml6YXRpb24gT24KICAg
IEVycm9yTG9nRm9ybWF0ICIle2N1fXQgJU0iCiAgICBFcnJvckxvZyAvdmFy
L2xvZy9hcGFjaGUyL2tleXN0b25lLmxvZwogICAgQ3VzdG9tTG9nIC92YXIv
bG9nL2FwYWNoZTIva2V5c3RvbmVfYWNjZXNzLmxvZyBjb21iaW5lZAoKICAg
IDxEaXJlY3RvcnkgL3Vzci9iaW4+CiAgICAgICAgUmVxdWlyZSBhbGwgZ3Jh
bnRlZAogICAgPC9EaXJlY3Rvcnk+CjwvVmlydHVhbEhvc3Q+Cgo8VmlydHVh
bEhvc3QgKjozNTM1Nz4KICAgIFdTR0lEYWVtb25Qcm9jZXNzIGtleXN0b25l
LWFkbWluIHByb2Nlc3Nlcz01IHRocmVhZHM9MSB1c2VyPWtleXN0b25lIGdy
b3VwPWtleXN0b25lIGRpc3BsYXktbmFtZT0le0dST1VQfQogICAgV1NHSVBy
b2Nlc3NHcm91cCBrZXlzdG9uZS1hZG1pbgogICAgV1NHSVNjcmlwdEFsaWFz
IC8gL3Vzci9iaW4va2V5c3RvbmUtd3NnaS1hZG1pbgogICAgV1NHSUFwcGxp
Y2F0aW9uR3JvdXAgJXtHTE9CQUx9CiAgICBXU0dJUGFzc0F1dGhvcml6YXRp
b24gT24KICAgIEVycm9yTG9nRm9ybWF0ICIle2N1fXQgJU0iCiAgICBFcnJv
ckxvZyAvdmFyL2xvZy9hcGFjaGUyL2tleXN0b25lLmxvZwogICAgQ3VzdG9t
TG9nIC92YXIvbG9nL2FwYWNoZTIva2V5c3RvbmVfYWNjZXNzLmxvZyBjb21i
aW5lZAoKICAgIDxEaXJlY3RvcnkgL3Vzci9iaW4+CiAgICAgICAgUmVxdWly
ZSBhbGwgZ3JhbnRlZAogICAgPC9EaXJlY3Rvcnk+CjwvVmlydHVhbEhvc3Q+
Cgo=
====
EOF

a2enmod wsgi

ln -sf /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled

rm -f /var/lib/keystone/keystone.db
""")

    ServiceControl.launch("apache2", "wsgi:keystone")

