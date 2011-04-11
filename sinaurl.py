#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sinaurl.py resolves sinaurl.cn urls and saves the link to a database

import sys
import pg
#import simplejson
import time
import string
import types
import pycurl
import re

import mypass

usage = "sinaurl.py [url] "

def getLocation(buf):
    if buf.startswith("Location:"):
	realurl = string.replace(buf, "Location: ", "", 1)
	realurl = string.strip(realurl)
	print myurl
	m = re.match(r"http://([a-zA-Z0-9\-\.]+)/", myurl)
	try:
	    baseurl = m.group(1)
	except IndexError:
	    baseurl = ""
	hashurl = string.replace(myurl, "http://" + baseurl + "/", "", 1)
	sinaurl = { "hash": hashurl, "location": realurl, "base": baseurl }
	try:
	    print sinaurl
	    pgconn = mypass.getConn()
	    pgconn.insert("sinaweibo_sinaurl", sinaurl)
	except pg.ProgrammingError:
	    pass
	print realurl
	#sys.exit()

def sinaurl(url):
    global myurl
    if url is None:
	return 0
    myurl = url
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, 0)
    c.setopt(pycurl.HEADERFUNCTION, getLocation)
    c.perform()
    c.close()

if __name__ == "__main__":
    myurl = ""
    if len(sys.argv) < 2:
	print usage
	sys.exit()
    else:
	url = sys.argv[1]
    sinaurl(url)
