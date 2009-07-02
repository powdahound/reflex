import os
import time
from twisted.python import log
from pyrrd.rrd import DataSource, RRA, RRD

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
        rrd = RRD(filename, ds=dss, rra=rras, start=now-60)
        rrd.create()
        return rrd

    def getRRD(self):
        dir = '/var/reflex/rrds'
        filename = "%s/%s_%s.rrd" % (dir, self.key, TYPE_NAMES[self.type])
        rrd = None

        # make sure /rrds directory is there for us
        if not os.path.exists(dir):
            os.makedirs(dir)

        if not os.path.isfile(filename):
            rrd = self.createRRD(filename)
        else:
            rrd = RRD(filename)

        return rrd

    def getFilename(self):
        rrd = self.getRRD()
        return rrd.filename

    def rollup(self):
        pass

    def save(self, value):
        value = int(value)
        print 'Updating %s with value: %d' % (self.getFilename(), value)
        now = int(time.time())
        rrd = self.getRRD()
        rrd.bufferValue(now, value)
        try:
            rrd.update()
        except IOError, e:
            # TODO: Figure out what's actually causing this exception
            log.msg('ERROR: IOError caught while updating RRD (%s): %s' \
                    % (self.getFilename(), e))

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
