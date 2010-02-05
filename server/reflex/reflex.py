from twisted.application import internet
from twisted.internet import protocol, reactor, task
from twisted.python import log

from txredis.protocol import Redis

import stats


class ReflexProtocol(protocol.DatagramProtocol):
    noisy = True

    def __init__(self):
        """Note: Parent class has no __init__ to call"""
        self.rollup_task = None
        self.stats = {}
        self.redis = None

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
                self.stats[full_key] = stats.SumStat(self, key)
            elif type == stats.TYPE_AVERAGE:
                self.stats[full_key] = stats.AverageStat(self, key)
            else:
                log.msg('Unknown stat type: %s' % type)
                return None

        return self.stats[full_key]

    def startProtocol(self):
        protocol.DatagramProtocol.startProtocol(self)

        # start data rollup task
        self.rollup_task = task.LoopingCall(self.rollupData)
        self.rollup_task.start(60, now=False)

        # connect to redis
        cc = protocol.ClientCreator(reactor, Redis)
        d = cc.connectTCP('localhost', 6379)

        def cb(result):
            self.redis = result
            log.msg('Connected to Redis: %r' % self.redis)

        d.addCallback(cb)
        return d

    def stopProtocol(self):
        protocol.DatagramProtocol.stopProtocol(self)

    def rollupData(self):
        for stat in self.stats:
            self.stats[stat].rollup()


class ReflexService(internet.UDPServer):

    def startService(self):
        internet.UDPServer.startService(self)
        log.msg('Reflex service ready and waiting!')
