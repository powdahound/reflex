import os
import socket
import time
from collectd_unixsock import Collectd
from twisted.python import log
from datetime import datetime

# Stat types supported
TYPE_SUM = 1
TYPE_AVERAGE = 2


class Stat:
    type = None

    def __init__(self, core, key):
        self.collectd = Collectd()
        self.data = []
        self.key = key
        self.core = core

    def rollup(self):
        pass

    def send_to_collectd(self, value):
        value = int(value)
        #print 'Sending %s = %d' % (self.key, value)

        # send to collectd
        hostname = socket.getfqdn()
        id = "%s/reflex/gauge-%s" % (hostname, self.key)
        self.collectd.putval(id, ['U', value], { 'interval': 60 })

    def send_to_redis(self, value):
        # increase redis counter
        if value:
            hour = datetime.utcnow().strftime('%Y%m%d%H')
            key = "%s_%s" % (self.key, hour)
            # log.msg('Incrementing in redis: %r by %d' % (key, value))

            if not self.core.redis:
                log.msg("Redis not available")
                return

            self.core.redis.incr(key, value)
            self.core.redis.sadd('reflex_stats', self.key)

    def update(self, data):
        #print 'Updating %s with %s' % (self.key, data)
        pass


class SumStat(Stat):
    type = TYPE_SUM

    def rollup(self):
        # save for collectd
        count = 0
        local_data = list(self.data)
        self.data = []
        for num in local_data:
            count += num

        self.send_to_collectd(count)
        #self.send_to_redis(count)

    def update(self, data):
        self.data.append(int(data))


class AverageStat(Stat):
    type = TYPE_AVERAGE

    def rollup(self):
        sum = 0
        local_data = list(self.data)
        self.data = []

        for num in local_data:
            sum += num

        if len(local_data) > 0:
            average = (sum / len(local_data))
        else:
            average = 0

        self.send_to_collectd(average)

    def update(self, data):
        self.data.append(int(data))
