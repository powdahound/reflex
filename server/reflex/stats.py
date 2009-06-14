import os
from twisted.python import log
from pyrrd import rrd

# Stat types supported
TYPE_SUM     = 1
TYPE_AVERAGE = 2

# Human names for each type
TYPE_NAMES = {
  TYPE_SUM:     'sum',
  TYPE_AVERAGE: 'average',
}

class Stat:
  type = None

  def __init__(self, key):
    self.key = key
    self.data = []

  def createRRD(self, filename):
    # TODO: Format the RRD correctly
    log.msg('Creating RRD: %s' % filename)
    dss = []
    rras = []
    dss.append(rrd.DataSource(ds_name=self.key, ds_type='GAUGE', heartbeat=60))
    rras.append(rrd.RRA(cf='AVERAGE', xff=0.5, steps=1, rows=24))
    rras.append(rrd.RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10))
    rrd = rrd.RRD(filename, ds=dss, rra=rras, start=920804400)
    rrd.create()
    return rrd

  def getRRD(self):
    # TODO: Use /var/reflex/rrds or something as dir
    dir = '/tmp'
    filename = "%s/%s_%s.rrd" % (dir, self.key, TYPE_NAMES[self.type])
    rrd = None

    if not os.path.isfile(filename):
      rrd = self.createRRD(filename)
    else:
      rrd = rrd.RRD(filename)

    return rrd

  def rollup(self):
    pass

  def save(self, value):
    print 'Updating %s RRD with value: %s' % (self.key, value)

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
    print 'Storing data: %s' % data
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
