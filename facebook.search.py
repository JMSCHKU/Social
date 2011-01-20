#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import re
import json
import csv
#import time
import datetime
import httplib
import urllib

import mypass

usage = "usage: facebook.search.py [type=user,post,page,event,group] [query string] [-h|--http-header|-co|--csv-out|-d|--database\
|-t OBJTYPE|--type=OBJTYPE|-c OBJTYPE|--connection-type=CONNTYPE] "

pgconn = mypass.getConn()

FB_GRAPH_API = "graph.facebook.com"
fbook_oauth = mypass.getFacebookOauth()
APP_ID = str(fbook_oauth["app_id"])
ACCESS_TOKEN = fbook_oauth["access_token"]

if __name__ == "__main__":
    q = ""
    showheader = False
    csvout = False
    database = True
    allfields = False
    if len(sys.argv) > 2:
	fbobjtype = sys.argv[1]
	for i in range(2, len(sys.argv)):
	    if sys.argv[i].startswith("-"):
		break
	    if q != "":
		q += " "
	    q += str(sys.argv[i])
	for j in range(i, len(sys.argv)):
    	    if sys.argv[j] == "-h" or sys.argv[j] == "--http-header":
		showheader = True
	    if sys.argv[j] == "-co" or sys.argv[j] == "--csv-out":
		csvout = True
	    if sys.argv[j] == "-no" or sys.argv[j] == "--no-overwrite":
		allowUpdate = False
	    if sys.argv[j] == "-d" or sys.argv[j] == "--database":
		database = True
	    if sys.argv[j] == "-a" or sys.argv[j] == "--all-fields":
		allfields = True
    else:
	print usage
	sys.exit()

    # get the parameters
    params = dict()
    params['access_token'] = APP_ID + "|" + ACCESS_TOKEN
    #params['metadata'] = 1
    params["q"] = q
    params["type"] = fbobjtype

    # form the url
    url = "/search?%s" % urllib.urlencode(params)

    # try to connect
    conn = httplib.HTTPSConnection(FB_GRAPH_API)
    try:
	conn.request("GET", url)
	#resp, content = conn.request(url, "GET")
    except Exception:
	print Exception
	sys.exit(sys.exc_info())

    # get the response
    r = conn.getresponse()

    # print status code and headers
    if showheader:
	print "https://" + FB_GRAPH_API + url
	print r.status, r.reason
	print r.getheaders()

    # load the response as json string
    js = json.loads(r.read())

    print js
