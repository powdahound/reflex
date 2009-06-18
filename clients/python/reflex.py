import socket

# Stat types
TYPE_SUM = 1
TYPE_AVERAGE = 2

class ReflexClient:
  def __init__(self, host, port=7828):
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def send(self, type, key, value):
    msg = "%d %s %d" % (type, key, value)
    self.sock.sendto(msg, (self.host, self.port))

  def sendSum(self, key, value=1):
    self.send(TYPE_SUM, key, value)

  def sendAverage(self, key, value):
    self.send(TYPE_AVERAGE, key, value)

if __name__ == "__main__":
  print "Sending test stats to 127.0.0.1"
  client = ReflexClient('127.0.0.1')
  client.sendSum('sum_foo')
  client.sendAverage('average_foo', 5)
