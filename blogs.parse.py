#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import mypass
import datetime
import time
import rfc822
import urllib2
import httplib
from xml.dom import minidom

try:
    blogid = int(sys.argv[1])
except:
    print "Missing blog ID"
    sys.exit()

try:
    url = sys.argv[2]
except:
    print "Missing URL"
    sys.exit()

p = urllib2.urlopen(url, timeout=30)
txt = p.read()

try:
    dom = minidom.parseString(txt)
except Exception as e:
    print e
    print "Invalid URL: " + url

pgconn = mypass.getConn()

for item in dom.getElementsByTagName('item'):
    r = dict()
    r["blogid"] = blogid
    for a in ["title", "link", "guid", "description", "author", "comments", "category"]:
	att = None
	try:
	    att = item.getElementsByTagName(a)[0].firstChild.data
	    r[a] = att.encode("utf8")
	except:
	    #print "does not exist: " + a
	    r[a] = att
    try:
	pubDate = item.getElementsByTagName("pubDate")[0].firstChild.data
	#pubDate_dt = datetime.datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %z')
	#print pubDate
	try:
	    pubDate_dt = rfc822.parsedate_tz(pubDate)
	    pubDate_str = time.strftime("%Y-%m-%d %H:%M:%S", pubDate_dt[0:9])
	    tz = pubDate.split()
	    tz_str = tz[len(tz)-1]
	    r["pubdate"] = pubDate_str + " " + tz_str
	except:
	    try:
		r["pubdate"] = pubDate.replace("/","-") + " +0800"
	    except:
		r["pubdate"] = pubDate + " +0800"
	#print r
    except Exception as e:
	print e
	continue
    try:
	pgconn.insert("blogs_entries", r)
    except Exception as e:
	print e
	continue

pgconn.close()
