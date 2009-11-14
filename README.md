Reflex is a system which allows you to monitor live applications without parsing logs or counting values in your code. Reflex clients send UDP packets to a central server which aggregates the data and sends it to [Collectd][cd] every minute. My hope is that this support is added to Collectd's [UnixSock][us] plugin [in the future][ei].

It was inspired by [Flickr-StatsD][fsd] which is [explained here][fct].

  [fct]: http://code.flickr.com/blog/2008/10/27/counting-timing/
  [fsd]: http://code.flickr.com/trac/browser/trunk/Flickr-StatsD
  [rrd]: http://oss.oetiker.ch/rrdtool/
  [tw]: http://twistedmatrix.com/
  [cd]: http://collectd.org/
  [us]: http://collectd.org/wiki/index.php/Plugin:UnixSock
  [ei]: http://collectd.org/wiki/index.php/Roadmap#Event_infrastructure
