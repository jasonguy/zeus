
import yaml

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

class ConfigParser(object):
    def __enter__(self):
        return True

    def __exit__(self, type, value, traceback):
        return True

    def __init__(self):
        return

    def __slurp(self, yamlfile, section_name):
        with open(yamlfile, 'r') as yaml_file:
            yamldata = yaml.load(yaml_file.read())

        if yamldata and section_name in yamldata:
            return yamldata[section_name]
        else:
            return {}

    def parse(self, yamlfile, section_name):
        return self.__slurp(yamlfile, section_name)

class ConfigManager(object):
    def __enter__(self):
        return True

    def __exit__(self, type, value, traceback):
        return True

    def __init__(self, configfile):
        self.__setup(configfile)

    def __setup(self, configfile):
        self._config = ConfigParser().parse(configfile, 'config')
        self._roles = ConfigParser().parse(configfile, 'roles')
        self._servers = ConfigParser().parse(configfile, 'servers')

    @property
    def config(self):
        return self._config

    @property
    def roles(self):
        return self._roles

    @property
    def servers(self):
        return self._servers
