import os
import socket
import time
from collectd_unixsock import Collectd
from pyrrd.rrd import DataSource, RRA, RRD
from twisted.python import log

# Stat types supported
TYPE_SUM = 1
TYPE_AVERAGE = 2

# Human names for each type
TYPE_NAMES = {
  TYPE_SUM: 'sum',
  TYPE_AVERAGE: 'average',
}


class Stat:
    type = None

    def __init__(self, key):
        self.key = key
        self.data = []
        self.rrd = None
        self.collectd = Collectd()

    def createRRD(self, filename):
        """Create an RRD file for a stat

        A good explanation of RRD creation can be found here:
          http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html

        RRA values were generated using http://rrdtools.appspot.com.
        The RRAs we create are:
          - 1m  for 24h
          - 15m for 30d
          - 1d  for 5y

        """
        log.msg('Creating RRD: %s' % filename)
        now = int(time.time())
        dss = []
        rras = []
        dss.append(DataSource(dsName=self.key, dsType='GAUGE', heartbeat=300))
        rras.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=1440))
        rras.append(RRA(cf='AVERAGE', xff=0.5, steps=15, rows=2880))
        rras.append(RRA(cf='AVERAGE', xff=0.5, steps=1440, rows=1826))
        try:
            rrd = RRD(filename, ds=dss, rra=rras, start=now-60)
            rrd.create()
            return rrd
        except:
            log.msg('ERROR: some exception while creating rrd. grr')
            return None

    def getRRD(self):
        if not self.rrd:
            dir = '/var/reflex/rrds'
            filename = "%s/%s_%s.rrd" % (dir, self.key, TYPE_NAMES[self.type])
            print 'Getting handle to RRD: %s' % filename

            # make sure /rrds directory is there for us
            if not os.path.exists(dir):
                os.makedirs(dir)

            if not os.path.isfile(filename):
                self.rrd = self.createRRD(filename)
            else:
                self.rrd = RRD(filename)

        return self.rrd

    def getFilename(self):
        rrd = self.getRRD()
        return rrd.filename if rrd else None

    def rollup(self):
        pass

    def save(self, value):
        value = int(value)
        print 'Updating %s with value: %d' % (self.getFilename(), value)

        # send to collectd
        hostname = socket.getfqdn()
        id = "%s/reflex/gauge-%s" % (hostname, self.key)
        self.collectd.putval(id, ['U', value], { 'interval': 60 })

        # legacy: write our rrd
        rrd = self.getRRD()
        if not rrd:
            print "ERROR: Could not get RRD for key=%s" % self.key
            return
        now = int(time.time())
        rrd.bufferValue(now, value)
        try:
            rrd.update()
        except EnvironmentError, e:
            # TODO: Figure out what's actually causing this exception
            log.msg('ERROR: EnvironmentError caught while \
                    updating RRD (%s): %s' % (self.getFilename(), e))

    def update(self, data):
        print 'Updating %s with %s' % (self.key, data)


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
