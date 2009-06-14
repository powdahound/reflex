from twisted.application import internet
from twisted.internet import protocol, task
from twisted.python import log

import stats

class ReflexProtocol(protocol.DatagramProtocol):
  noisy = True

  def __init__(self):
    """Note: Parent class has no __init__ to call"""
    self.rollup_task = None
    self.stats = {}

  def datagramReceived(self, data, (host, port)):
    data = data.strip()
    type, key, args = data.split()
    stat = self.getStat(type, key)
    if stat:
      stat.update(args)

  def getStat(self, type, key):
    full_key = "%s_%s" % (type, key)
    type = int(type)

    if full_key not in self.stats:
      # TODO: Switch to dynamic dispatch or something
      if type == stats.TYPE_SUM:
        self.stats[full_key] = stats.SumStat(key)
      elif type == stats.TYPE_AVERAGE:
        self.stats[full_key] = stats.AverageStat(key)
      else:
        log.msg('Unknown stat type: %s' % type)
        return None

    return self.stats[full_key]

  def startProtocol(self):
    protocol.DatagramProtocol.startProtocol(self)

    # start data rollup task
    self.rollup_task = task.LoopingCall(self.rollupData)
    self.rollup_task.start(6, now=False)

  def stopProtocol(self):
    protocol.DatagramProtocol.stopProtocol(self)
    self.rollup_task.stop()

  def rollupData(self):
    log.msg('Rolling up data...')
    for stat in self.stats:
      self.stats[stat].rollup()

class ReflexService(internet.UDPServer):
  def startService(self):
    internet.UDPServer.startService(self)
    log.msg('Reflex service ready and waiting!')
