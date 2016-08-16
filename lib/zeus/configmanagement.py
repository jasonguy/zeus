
from fabric.api import run

class ConfigEditor(object):
    def __init__(self):
        return

    @classmethod
    def setKey(cls, configfile, section, key, value):
        run("""
/usr/share/zeus/bin/xkv.py set "%s" "%s" "%s" "%s"
""" % (configfile, section, key, value))

