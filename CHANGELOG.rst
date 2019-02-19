0.1.4 - 20-Feb-2019
-------------------

* Fix ``ip2geotools.databases.commercial.Ip2LocationWeb`` by using ``selenium`` with Firefox because of new webpage layout
* Better exception handling in ``ip2geotools.databases.noncommercial.Ipstack``

0.1.3 - 27-Nov-2018
-------------------

* New ``ip2geotools.databases.commercial.Ipdata`` requested by Jonathan Kosgei from ipdata.co
* New ``ip2geotools.databases.noncommercial.Ipstack`` as a replacement for ``ip2geotools.databases.noncommercial.Freegeoip``
* Fix ``ip2geotools.databases.commercial.DbIpWeb`` because of new webpage layout
* Fix ``ip2geotools.databases.commercial.Ip2LocationWeb`` because of new webpage layout
* Fix ``ip2geotools.databases.commercial.NeustarWeb`` because of new URL
* Default free api key in ``ip2geotools.databases.noncommercial.DbIpCity``
* ``ip2geotools.databases.noncommercial.Freegeoip`` is deprecated!

0.1.2 - 30-Nov-2017
-------------------

* Fix ``ip2geotools.databases.commercial.DbIpWeb`` because of new webpage layout
* "IP address not found" error can be recognized in ``ip2geotools.databases.commercial.SkyhookContextAcceleratorIp``
* Custom exceptions can be formatted in ``ip2geotools.errors``

0.1.1 - 01-Nov-2017
-------------------

* Fix installation from PyPi using ``pip``

0.1 - 01-Nov-2017
-----------------

* First release
