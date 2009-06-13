from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from reflex import ReflexProtocol, ReflexService

class Options(usage.Options):
  optParameters = [
    ["port", "p", 7828, "The port number to listen on.", int]
  ]

class ReflexServiceMaker(object):
  implements(IServiceMaker, IPlugin)
  tapname = "reflex"
  description = "A Reflex server."
  options = Options

  def makeService(self, options):
    return ReflexService(int(options['port']), ReflexProtocol())

serviceMaker = ReflexServiceMaker()
