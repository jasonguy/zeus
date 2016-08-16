
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
@roles('openstack_compute')
def nova_compute():
    RepoManager.install("nova-compute")

    keystone_server = metadata.roles['openstack_keystone'][0]
    keystone_ip = metadata.servers[keystone_server]['ip']

    controller = metadata.roles['openstack_controller'][0]
    controller_ip = metadata.servers[controller]['ip']

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

    for key in keystone_configs:
        ConfigEditor.setKey(
            config_file,
            "keystone_authtoken",
            key,
            keystone_configs[key])

    neutron_configs = {
        'url': 'http://%s:9696' % neutron_ip,
        'auth_url': 'http://%s:35357' % keystone_ip,
        'auth_type': 'password',
        'project_domain_name': 'default',
        'user_domain_name': 'default',
        'region_name': 'RegionOne',
        'project_name': 'service',
        'username': 'neutron',
        'password': passwords["NEUTRON_PASS"]}

    for key in neutron_configs:
        ConfigEditor.setKey(
            config_file,
            "neutron",
            key,
            neutron_configs[key])

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
        "0.0.0.0")

    ConfigEditor.setKey(
        config_file,
        "vnc",
        "vncserver_proxyclient_address",
        my_ip)

    ConfigEditor.setKey(
        config_file,
        "vnc",
        "enabled",
        "True")

    ConfigEditor.setKey(
        config_file,
        "vnc",
        "novncproxy_base_url",
        "http://%s:6080/vnc_auto.html" % controller_ip)

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

    kvm_cores = int(run("""egrep -c '(vmx|svm)' /proc/cpuinfo"""))
    kvm_active = run("""grep kvm /proc/misc""")

    if kvm_cores == 0 or kvm_active == '':
        ConfigEditor.setKey(
            "/etc/nova/nova-compute.conf",
            "libvirt",
            "virt_type",
            "qemu")
    else:
        ConfigEditor.setKey(
            "/etc/nova/nova-compute.conf",
            "libvirt",
            "virt_type",
            "kvm")

    ServiceControl.launch("nova-compute")

