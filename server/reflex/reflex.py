from twisted.application import internet
from twisted.internet import protocol, task
from twisted.python import log

class ReflexProtocol(protocol.DatagramProtocol):
  noisy = True

  def datagramReceived(self, data, (host, port)):
    log.msg('Got data: %s' % data.strip())
    self.transport.write('Thanks!\n', (host, port))

class ReflexService(internet.UDPServer):
  def startService(self):
    internet.UDPServer.startService(self)
    log.msg('Reflex service ready and waiting!')

    # start data rollup task
    rollup_task = task.LoopingCall(self.rollupData)
    rollup_task.start(60, now=False)

  def rollupData(self):
    log.msg('Rolling up data...')
