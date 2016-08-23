
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
@roles('openstack_neutron')
def neutron():

    run("""
NEUTRON_PASS="%s"
NEUTRON_IP="%s"
MIDONET_PASS="%s"

. admin-openrc

openstack user list | grep neutron || openstack user create --domain default --password "${NEUTRON_PASS}" neutron
openstack user list | grep neutron && openstack user set --password "${NEUTRON_PASS}" neutron
openstack role add --project service --user neutron admin

openstack user list | grep midonet || openstack user create --domain default --password "${MIDONET_PASS}" midonet
openstack user list | grep neutron && openstack user set --password "${MIDONET_PASS}" midonet
openstack role add --project service --user midonet admin

openstack service list | grep neutron || openstack service create --name neutron --description "OpenStack Networking" network

openstack endpoint list | grep network | grep public   || openstack endpoint create --region RegionOne network public http://$NEUTRON_IP:9696
openstack endpoint list | grep network | grep internal || openstack endpoint create --region RegionOne network internal http://$NEUTRON_IP:9696
openstack endpoint list | grep network | grep admin    || openstack endpoint create --region RegionOne network admin http://$NEUTRON_IP:9696

""" % (
        passwords["NEUTRON_PASS"],
        metadata.servers[metadata.roles['openstack_neutron'][0]]['ip'],
        passwords["MIDONET_PASS"]))

    RepoManager.install("neutron-server")
    RepoManager.install("python-networking-midonet")
    RepoManager.install("python-neutronclient")
    RepoManager.install("python-memcache")

    run("""
apt-get -y -u purge neutron-plugin-ml2
""")

    mysql_server = metadata.roles['openstack_mysql'][0]
    mysql_ip = metadata.servers[mysql_server]['ip']

    rabbit_server = metadata.roles['openstack_rabbitmq'][0]
    rabbit_ip = metadata.servers[rabbit_server]['ip']

    keystone_server = metadata.roles['openstack_keystone'][0]
    keystone_ip = metadata.servers[keystone_server]['ip']

    controller = metadata.roles['openstack_controller'][0]
    controller_ip = metadata.servers[controller]['ip']

    midonet_cluster = metadata.roles['midonet_cluster'][0]
    midonet_ip = metadata.servers[midonet_cluster]['ip']

    config_file = '/etc/neutron/neutron.conf'

    ConfigEditor.setKey(
        config_file,
        "database",
        "connection",
        "mysql+pymysql://neutron:%s@%s/neutron" % (
            passwords["NEUTRON_DBPASS"],
            mysql_ip))

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

    ConfigEditor.setKey(
        config_file,
        "DEFAULT",
        "auth_strategy",
        "keystone")

    keystone_configs = {
        'auth_uri': 'http://%s:5000' % keystone_ip,
        'auth_url': 'http://%s:35357' % keystone_ip,
        'memcached_servers': '%s:11211' % controller_ip,
        'auth_type': 'password',
        'project_domain_name': 'default',
        'user_domain_name': 'default',
        'project_name': 'service',
        'username': 'neutron',
        'password': passwords["NEUTRON_PASS"]}

    for key in keystone_configs:
        ConfigEditor.setKey(
            config_file,
            "keystone_authtoken",
            key,
            keystone_configs[key])

    nova_configs = {
        'auth_url': 'http://%s:35357' % keystone_ip,
        'auth_type': 'password',
        'project_domain_name': 'default',
        'user_domain_name': 'default',
        'project_name': 'service',
        'username': 'nova',
        'password': passwords["NOVA_PASS"]}

    for key in nova_configs:
        ConfigEditor.setKey(
            config_file,
            "nova",
            key,
            nova_configs[key])

    neutron_configs = {
        'rpc_backend': 'rabbit',
        'core_plugin': 'midonet.neutron.plugin_v2.MidonetPluginV2',
        'service_plugins': 'midonet.neutron.services.l3.l3_midonet.MidonetL3ServicePlugin',
        'notify_nova_on_port_status_changes': 'True',
        'notify_nova_on_port_data_changes': 'True',
        'dhcp_agent_notification': 'False',
        'allow_overlapping_ips': 'True',
        'nova_url': 'http://%s:8774/v2.1' % controller_ip}

    for key in neutron_configs:
        ConfigEditor.setKey(
            config_file,
            "DEFAULT",
            key,
            neutron_configs[key])

    run("""
mkdir -pv /etc/neutron/plugins/midonet

cat >/etc/default/neutron-server<<EOF
NEUTRON_PLUGIN_CONFIG="/etc/neutron/plugins/midonet/midonet.ini"
EOF

cat >/etc/neutron/plugins/midonet/midonet.ini<<EOF
[MIDONET]
midonet_uri = http://%s:8181/midonet-api
username = midonet
password = %s
project_id = service
EOF

su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/midonet/midonet.ini upgrade head" neutron
su -s /bin/sh -c "neutron-db-manage --subproject networking-midonet upgrade head" neutron
""" % (
        midonet_ip,
        passwords["MIDONET_PASS"]
    ))

    ServiceControl.launch("neutron-server")

