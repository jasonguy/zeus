
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

