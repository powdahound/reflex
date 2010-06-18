Reflex
======

**This is currently just an experimental project for messing around with stats stuff.**

Reflex is a system which allows you to monitor live applications without parsing logs or counting values in your code. Reflex clients (your apps) send UDP packets to a Reflex service which rolls up the data and sends it to other services every minute.

Currently, Reflex sends data to [Collectd][cd] for graphing and [Redis][rd] for storage (so accurate counts can be fetched).

[In the future][ei], I'd like Collectd's [UnixSock][us] plugin to accept packets directly so an intermediate service like this wouldn't be needed.

Reflex was originally inspired by [Flickr-StatsD][fsd] which is [explained here][fct].

To-Do
-----

 * Distutils install script for server
 * Reconnecting Redis class
 * Use txRedis
 * Drop collectd support
 * Store more data in Redis
 * Use Google visualization API for display
 * Small web UI
 * Include ability to delete/clear data points


  [fct]: http://code.flickr.com/blog/2008/10/27/counting-timing/
  [fsd]: http://code.flickr.com/trac/browser/trunk/Flickr-StatsD
  [rrd]: http://oss.oetiker.ch/rrdtool/
  [tw]: http://twistedmatrix.com/
  [cd]: http://collectd.org/
  [us]: http://collectd.org/wiki/index.php/Plugin:UnixSock
  [ei]: http://collectd.org/wiki/index.php/Roadmap#Event_infrastructure
  [rd]: http://code.google.com/p/redis
