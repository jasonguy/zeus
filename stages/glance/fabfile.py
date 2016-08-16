
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

#
# http://docs.openstack.org/mitaka/install-guide-ubuntu/glance-install.html
#
@parallel
@roles('openstack_glance')
def glance():
    run("""
GLANCE_PASS="%s"
GLANCE_IP="%s"

. admin-openrc

openstack user list | grep glance || openstack user create --domain default --password "${GLANCE_PASS}" glance
openstack user list | grep glance && openstack user set --password "${GLANCE_PASS}" glance
openstack role add --project service --user glance admin

openstack service list | grep glance || openstack service create --name glance --description "OpenStack Image" image

openstack endpoint list | grep image | grep public   || openstack endpoint create --region RegionOne image public http://$GLANCE_IP:9292
openstack endpoint list | grep image | grep internal || openstack endpoint create --region RegionOne image internal http://$GLANCE_IP:9292
openstack endpoint list | grep image | grep admin    || openstack endpoint create --region RegionOne image admin http://$GLANCE_IP:9292

""" % (
        passwords["GLANCE_PASS"],
        metadata.servers[metadata.roles['openstack_glance'][0]]['ip']))

    RepoManager.install("glance")

    ConfigEditor.setKey(
        "/etc/glance/glance-api.conf",
        "glance_store",
        "stores",
        "file,http")

    ConfigEditor.setKey(
        "/etc/glance/glance-api.conf",
        "glance_store",
        "default_store",
        "file")

    ConfigEditor.setKey(
        "/etc/glance/glance-api.conf",
        "glance_store",
        "filesystem_store_datadir",
        "/var/lib/glance/images/")

    keystone_server = metadata.roles['openstack_keystone'][0]
    keystone_ip = metadata.servers[keystone_server]['ip']

    controller = metadata.roles['openstack_controller'][0]
    controller_ip = metadata.servers[controller]['ip']

    mysql_server = metadata.roles['openstack_mysql'][0]
    mysql_ip = metadata.servers[mysql_server]['ip']

    glance_keystone_configs = {
        'auth_uri': 'http://%s:5000' % keystone_ip,
        'auth_url': 'http://%s:35357' % keystone_ip,
        'memcached_servers': '%s:11211' % controller_ip,
        'auth_type': 'password',
        'project_domain_name': 'default',
        'user_domain_name': 'default',
        'project_name': 'service',
        'username': 'glance',
        'password': passwords["GLANCE_PASS"]}

    for config_file in [
        '/etc/glance/glance-api.conf',
        '/etc/glance/glance-registry.conf']:
        ConfigEditor.setKey(
            config_file,
            "database",
            "connection",
            "mysql+pymysql://glance:%s@%s/glance" % (
                passwords["GLANCE_DBPASS"],
                mysql_ip))

        for key in glance_keystone_configs:
            ConfigEditor.setKey(
                config_file,
                "keystone_authtoken",
                key,
                glance_keystone_configs[key])

        ConfigEditor.setKey(
            config_file,
            "paste_deploy",
            "flavor",
            "keystone")

    run("""
su -s /bin/sh -c "glance-manage db_sync" glance
""")

    ServiceControl.launch("glance-registry")
    ServiceControl.launch("glance-api")

