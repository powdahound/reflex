from twisted.application import internet, service
from twisted.internet import protocol, reactor, task
from twisted.python import log

from txredis.protocol import Redis

import stats


class CoreService(service.MultiService):

    def __init__(self, reflex_port, redis_host, redis_port):
        service.MultiService.__init__(self)
        self.redis = None
        self.reflex_port = reflex_port
        self.redis_host = redis_host
        self.redis_port = redis_port

        # setup main service
        rs = ReflexService(self.reflex_port, ReflexProtocol(self))
        rs.setServiceParent(self)

    def startService(self):
        log.msg("Starting services...")
        log.msg(" - Reflex is localhost:%d" % self.reflex_port)
        #log.msg(" - Redis is %s:%d" % (self.redis_host, self.redis_port))

        service.MultiService.startService(self)

        # connect to redis
        #redis_factory = RedisFactory(self)
        #d = reactor.connectTCP(self.redis_host, self.redis_port, redis_factory)
        #return d


class ReflexProtocol(protocol.DatagramProtocol):
    noisy = True

    def __init__(self, core):
        """Note: Parent class has no __init__ to call"""
        self.rollup_task = None
        self.stats = {}
        self.core = core

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
                self.stats[full_key] = stats.SumStat(self.core, key)
            elif type == stats.TYPE_AVERAGE:
                self.stats[full_key] = stats.AverageStat(self.core, key)
            else:
                log.msg('Unknown stat type: %s' % type)
                return None

        return self.stats[full_key]

    def startProtocol(self):
        protocol.DatagramProtocol.startProtocol(self)

        # start data rollup task
        self.rollup_task = task.LoopingCall(self.rollupData)
        self.rollup_task.start(60, now=False)

    def stopProtocol(self):
        protocol.DatagramProtocol.stopProtocol(self)

    def rollupData(self):
        for stat in self.stats:
            self.stats[stat].rollup()


class ReflexService(internet.UDPServer):

    def startService(self):
        internet.UDPServer.startService(self)
        log.msg('Reflex service started')


class RedisFactory(protocol.ReconnectingClientFactory):
    def __init__(self, core):
        self.core = core
        parent = protocol.ReconnectingClientFactory

    def startedConnecting(self, connector):
        print 'Connecting to Redis...'

    def buildProtocol(self, addr):
        print 'Connected to Redis'
        self.resetDelay()

        protocol = Redis()
        self.core.redis = protocol
        return protocol

    def clientConnectionLost(self, connector, reason):
        print 'Lost Redis connection. Reason:', reason

        parent = protocol.ReconnectingClientFactory
        parent.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Redis connection failed. Reason:', reason

        parent = protocol.ReconnectingClientFactory
        parent.clientConnectionFailed(self, connector, reason)
