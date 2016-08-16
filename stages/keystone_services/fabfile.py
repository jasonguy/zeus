
import os

from zeus.config import ConfigManager
from zeus.common import FabricManager
from zeus.common import PasswordManager

from fabric.api import parallel, roles, run, env

metadata = ConfigManager(os.environ["CONFIGFILE"])

passwords = PasswordManager(os.environ["PASSWORDCACHE"]).passwords

FabricManager.setup(metadata.roles)

#
# http://docs.openstack.org/mitaka/install-guide-ubuntu/keystone-services.html
#
@parallel
@roles('openstack_keystone')
def keystone_services():
    run("""
export OS_TOKEN=%s
CONTROLLER="%s"
ADMIN_PASS="%s"
DEMO_PASS="%s"

export OS_URL=http://$CONTROLLER:35357/v3
export OS_IDENTITY_API_VERSION=3

openstack service list | grep 'keystone' | grep 'identity' || openstack service create --name keystone --description "OpenStack Identity" identity

openstack endpoint list | grep 'RegionOne' | grep 'keystone' | grep 'identity' | grep 'public'   || openstack endpoint create --region RegionOne identity public http://$CONTROLLER:5000/v3
openstack endpoint list | grep 'RegionOne' | grep 'keystone' | grep 'identity' | grep 'internal' || openstack endpoint create --region RegionOne identity internal http://$CONTROLLER:5000/v3
openstack endpoint list | grep 'RegionOne' | grep 'keystone' | grep 'identity' | grep 'admin'    || openstack endpoint create --region RegionOne identity admin http://$CONTROLLER:35357/v3

openstack domain list | grep 'default' || openstack domain create --description "Default Domain" default

openstack project list | grep admin   || openstack project create --domain default --description "Admin Project" admin
openstack project list | grep service || openstack project create --domain default --description "Service Project" service
openstack project list | grep demo    || openstack project create --domain default --description "Demo Project" demo

openstack user list --domain default | grep admin || openstack user create --domain default --password "${ADMIN_PASS}" admin
openstack user list --domain default | grep admin && openstack user set --password "${ADMIN_PASS}" admin

openstack role list | grep admin || openstack role create admin
openstack role add --project admin --user admin admin

openstack user list --domain default | grep demo || openstack user create --domain default --password "${DEMO_PASS}" demo
openstack user list --domain default | grep demo && openstack user set --password "${DEMO_PASS}" demo

openstack role list | grep user || openstack role create user
openstack role add --project demo --user demo user

""" % (
        passwords["ADMIN_TOKEN"],
        metadata.servers[env.host_string]['ip'],
        passwords["ADMIN_PASS"],
        passwords["DEMO_PASS"]))

