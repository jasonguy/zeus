
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
# http://docs.openstack.org/mitaka/install-guide-ubuntu/nova-controller-install.html
#
@parallel
@roles('openstack_controller')
def nova_controller():
    run("""
NOVA_PASS="%s"
NOVA_IP="%s"

. admin-openrc

openstack user list | grep nova || openstack user create --domain default --password "${NOVA_PASS}" nova
openstack user list | grep nova && openstack user set --password "${NOVA_PASS}" nova
openstack role add --project service --user nova admin

openstack service list | grep nova || openstack service create --name nova --description "OpenStack Compute" compute

openstack endpoint list | grep compute | grep public   || openstack endpoint create --region RegionOne compute public http://$NOVA_IP:8774/v2.1/%%\(tenant_id\)s
openstack endpoint list | grep compute | grep internal || openstack endpoint create --region RegionOne compute internal http://$NOVA_IP:8774/v2.1/%%\(tenant_id\)s
openstack endpoint list | grep compute | grep admin    || openstack endpoint create --region RegionOne compute admin http://$NOVA_IP:8774/v2.1/%%\(tenant_id\)s

""" % (
        passwords["NOVA_PASS"],
        metadata.servers[metadata.roles['openstack_controller'][0]]['ip']))

    RepoManager.install("nova-api")
    RepoManager.install("nova-conductor")
    RepoManager.install("nova-consoleauth")
    RepoManager.install("nova-novncproxy")
    RepoManager.install("nova-scheduler")

    keystone_server = metadata.roles['openstack_keystone'][0]
    keystone_ip = metadata.servers[keystone_server]['ip']

    controller = env.host_string
    controller_ip = metadata.servers[controller]['ip']

    mysql_server = metadata.roles['openstack_mysql'][0]
    mysql_ip = metadata.servers[mysql_server]['ip']

    rabbit_server = metadata.roles['openstack_rabbitmq'][0]
    rabbit_ip = metadata.servers[rabbit_server]['ip']

    glance_server = metadata.roles['openstack_glance'][0]
    glance_ip = metadata.servers[glance_server]['ip']

    my_ip = metadata.servers[env.host_string]['ip']

    keystone_configs = {
        'auth_uri': 'http://%s:5000' % keystone_ip,
        'auth_url': 'http://%s:35357' % keystone_ip,
        'memcached_servers': '%s:11211' % controller_ip,
        'auth_type': 'password',
        'project_domain_name': 'default',
        'user_domain_name': 'default',
        'project_name': 'service',
        'username': 'nova',
        'password': passwords["NOVA_PASS"]}

    config_file = '/etc/nova/nova.conf'

    ConfigEditor.setKey(
        config_file,
        "database",
        "connection",
        "mysql+pymysql://nova:%s@%s/nova" % (
            passwords["NOVA_DBPASS"],
            mysql_ip))

    ConfigEditor.setKey(
        config_file,
        "api_database",
        "connection",
        "mysql+pymysql://nova_api:%s@%s/nova_api" % (
            passwords["NOVA_API_DBPASS"],
            mysql_ip))


    for key in keystone_configs:
        ConfigEditor.setKey(
            config_file,
            "keystone_authtoken",
            key,
            keystone_configs[key])

    ConfigEditor.setKey(
        config_file,
        "DEFAULT",
        "enabled_apis",
        "osapi_compute,metadata")

    ConfigEditor.setKey(
        config_file,
        "DEFAULT",
        "auth_strategy",
        "keystone")

    ConfigEditor.setKey(
        config_file,
        "DEFAULT",
        "my_ip",
        my_ip)

    ConfigEditor.setKey(
        config_file,
        "DEFAULT",
        "use_neutron",
        "True")

    ConfigEditor.setKey(
        config_file,
        "DEFAULT",
        "firewall_driver",
        "nova.virt.firewall.NoopFirewallDriver")

    ConfigEditor.setKey(
        config_file,
        "vnc",
        "vncserver_listen",
        my_ip)

    ConfigEditor.setKey(
        config_file,
        "vnc",
        "vncserver_proxyclient_address",
        my_ip)

    ConfigEditor.setKey(
        config_file,
        "glance",
        "api_servers",
        "http://%s:9292" % glance_ip)

    ConfigEditor.setKey(
        config_file,
        "oslo_concurrency",
        "lock_path",
        "/var/lib/nova/tmp")

    ConfigEditor.setKey(
        config_file,
        "DEFAULT",
        "rpc_backend",
        "rabbit")

    ConfigEditor.setKey(
        config_file,
        "oslo_messaging_rabbit",
        "rabbit_host",
        rabbit_ip)

    ConfigEditor.setKey(
        config_file,
        "oslo_messaging_rabbit",
        "rabbit_userid",
        "openstack")

    ConfigEditor.setKey(
        config_file,
        "oslo_messaging_rabbit",
        "rabbit_password",
        passwords["RABBIT_PASS"])

    run("""
su -s /bin/sh -c "nova-manage api_db sync" nova
su -s /bin/sh -c "nova-manage db sync" nova
""")

    ServiceControl.launch("nova-api")
    ServiceControl.launch("nova-consoleauth")
    ServiceControl.launch("nova-scheduler")
    ServiceControl.launch("nova-conductor")
    ServiceControl.launch("nova-novncproxy")

