
from fabric.api import env

class FabricManager(object):
    def __init__(self):
        return

    @classmethod
    def setup(cls, roles):
        env.use_ssh_config = True

        env.port = 22
        env.connection_attempts = 5
        env.timeout = 5

        env.parallel = True
        env.roledefs = roles

class PasswordManager(object):
    def __init__(self, passwordfile):
        self._passwords = {}
        with open(passwordfile) as passwordcache:
            for line in passwordcache:
                name, var = line.partition("=")[::2]
                self._passwords[name.replace('export ', '')] = str(var).rstrip('\n')

    @property
    def passwords(self):
        return self._passwords

