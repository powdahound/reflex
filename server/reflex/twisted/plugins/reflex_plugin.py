from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from reflex import CoreService


class Options(usage.Options):
    optParameters = [
        ["port", "p", 7828, "The port number to listen on.", int],
        ["redis-host", "rh", "localhost", "Redis server host/ip.", str],
        ["redis-port", "rp", 6379, "Redis port.", int]]


class ReflexServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "reflex"
    description = "A Reflex server."
    options = Options

    def makeService(self, options):
        return CoreService(options['port'],
                           options['redis-host'],
                           options['redis-port'])

serviceMaker = ReflexServiceMaker()
