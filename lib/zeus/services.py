
from fabric.api import run

class ServiceControl(object):
    def __init__(self):
        return

    @classmethod
    def launch(cls, service_name, process_name):
        run("""
SERVICE_NAME="%s"
PROCESS_NAME="%s"

# update-rc.d "${SERVICE_NAME}" defaults
# /etc/init.d/"${SERVICE_NAME}" restart
# service "${SERVICE_NAME}" restart

systemctl restart "${SERVICE_NAME}"

for i in $(seq 1 120); do
    ps axufwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww | grep -v grep | grep "${PROCESS_NAME}" && break
    sleep 1
done

ps axufwwwwwwwww | grep -v grep | grep "${PROCESS_NAME}"

""" % (service_name, process_name))

class ServiceManager(object):
    def __init__(self):
        return

    @classmethod
    def services(cls):
        services = {}

        services["keystone"] = {}
        services["keystone"]["publicurl"] = "5000/v3"
        services["keystone"]["internalurl"] = "5000/v3"
        services["keystone"]["adminurl"] = "35357/v3"
        services["keystone"]["type"] = "identity"
        services["keystone"]["description"] = "OpenStack Identity"

        services["glance"] = {}
        services["glance"]["publicurl"] = "9292"
        services["glance"]["internalurl"] = "9292"
        services["glance"]["adminurl"] = "9292"
        services["glance"]["type"] = "image"
        services["glance"]["description"] = "OpenStack Image Service"

        services["nova"] = {}
        services["nova"]["publicurl"] = "8774/v2/%(tenant_id)s"
        services["nova"]["internalurl"] = "8774/v2/%(tenant_id)s"
        services["nova"]["adminurl"] = "8774/v2/%(tenant_id)s"
        services["nova"]["type"] = "compute"
        services["nova"]["description"] = "OpenStack Compute"

        services["neutron"] = {}
        services["neutron"]["publicurl"] = "9696"
        services["neutron"]["internalurl"] = "9696"
        services["neutron"]["adminurl"] = "9696"
        services["neutron"]["type"] = "network"
        services["neutron"]["description"] = "OpenStack Networking"

        services["swift"] = {}
        services["swift"]["publicurl"] = "8080/v1/AUTH_%(tenant_id)s"
        services["swift"]["internalurl"] = "8080/v1/AUTH_%(tenant_id)s"
        services["swift"]["adminurl"] = "8080"
        services["swift"]["type"] = "object-store"
        services["swift"]["description"] = "OpenStack Object Store"

        services["midonet"] = {}
        services["midonet"]["publicurl"] = "8181/midonet-api"
        services["midonet"]["internalurl"] = "8181/midonet-api"
        services["midonet"]["adminurl"] = "8181/midonet-api"
        services["midonet"]["type"] = "midonet"
        services["midonet"]["description"] = "MidoNet API Service"

        return services

