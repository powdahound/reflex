from twisted.internet import protocol

class ReflexProtocol(protocol.DatagramProtocol):
  def datagramReceived(self, data, (host, port)):
    print 'Got data: %s' % data.strip()
    self.transport.write('Thanks!\n', (host, port))
