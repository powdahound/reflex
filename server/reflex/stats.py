import os
import socket
import time
from collectd_unixsock import Collectd
from twisted.python import log

# Stat types supported
TYPE_SUM = 1
TYPE_AVERAGE = 2


class Stat:
    type = None

    def __init__(self, key):
        self.key = key
        self.data = []
        self.collectd = Collectd()

    def rollup(self):
        pass

    def save(self, value):
        value = int(value)
        #print 'Sending %s = %d' % (self.key, value)

        # send to collectd
        hostname = socket.getfqdn()
        id = "%s/reflex/gauge-%s" % (hostname, self.key)
        self.collectd.putval(id, ['U', value], { 'interval': 60 })

    def update(self, data):
        #print 'Updating %s with %s' % (self.key, data)
        pass


class SumStat(Stat):
    type = TYPE_SUM

    def rollup(self):
        sum = 0
        local_data = list(self.data)
        self.data = []
        for num in local_data:
            sum += num
        self.save(sum)

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

        self.save(average)

    def update(self, data):
        self.data.append(int(data))
