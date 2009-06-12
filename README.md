Overview
========================
Reflex is a system which allows you to monitor live applications without parsing logs or counting values in your code. Reflex clients send UDP packets to a central server which aggregates the data and generates [RRD][rrd] files.

It was inspired by [Flickr-StatsD][fsd] which is [explained here][fct].

**Reflex is a work in progress and is not yet ready for real usage!**

Installation
========================

Server
-------------------
The Reflex server runs on Linux and uses the excellent [Twisted][tw] networking library. It's not ready for installations just yet, so check back later!

Client
-------------------
Reflex clients are provided for PHP and Python but it's not too hard to write your own for any language that can send UDP packets.

  [fct]: http://code.flickr.com/blog/2008/10/27/counting-timing/
  [fsd]: http://code.flickr.com/trac/browser/trunk/Flickr-StatsD
  [rrd]: http://oss.oetiker.ch/rrdtool/
  [tw]: http://twistedmatrix.com/
