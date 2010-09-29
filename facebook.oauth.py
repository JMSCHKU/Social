#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import httplib
import simplejson

import oauth2 as oauth
import facebook
import pprint

import time
import datetime
import csv
import httplib2
import urllib

usage = "usage: facebook.oauth.py [0=get entity, 1=get friends, 2=get members] [Facebook ID or username] [-h|--http-header]"
pgconn = pg.DB('jmsc', '127.0.0.1', 5432, None, None, 'jmsc', 'YOUR_PASSWORD')

FB_GRAPH_API = "https://graph.facebook.com/"
app_id = "153838781304293"
access_token = "700fb2d817022f54b33e5f72-533415389|GlBuoIcBtHqDiapgBl_wQ9sXlog"

fbid = 0
fbname = ""
showheader = False

if len(sys.argv) > 2:
    try:
	opt = int(sys.argv[1])
    except ValueError:
	print usage
	sys.exit()
else:
    print usage
    sys.exit()

if len(sys.argv) > 2:
    if opt >= 0:
	try:
	    fbid = int(sys.argv[2])
	    #screen_name = str(sys.argv[2])
	except ValueError:
	    fbid = 0
	    fbname = sys.argv[2]
try:
    if len(fbname) > 0:
	fbidname = fbname
    else:
	fbidname = fbid
    if opt == 0: 
	fbconntype = ""
    	#res = pgconn.get("twitter_users", { "screen_name": screen_name }, "screen_name")
	#if len(res) > 0:
	#    print "duplicate has been found: this script will exit..."
	#    sys.exit()
    elif opt == 1:
	fbconntype = "friends"
    elif opt == 2:
	fbconntype = "members"
    else:
	print usage
	sys.exit()
except pg.DatabaseError:
    pass

if len(sys.argv) > 3:
    for i in range(3,len(sys.argv)):
	if sys.argv[i] == "-h" or sys.argv[i] == "--http-header":
    	    showheader = True

params = dict()
params['access_token'] = app_id + "|" + access_token

url = FB_GRAPH_API + str(fbidname) + "/" + fbconntype
url = url + "?%s" % urllib.urlencode(params)

print url

req = oauth.Request(method="GET", url=url, parameters=params)

pp = pprint.PrettyPrinter(indent=4)

h = httplib2.Http()

if opt <= 3:
    resp, content = h.request(url, "GET")
    js = simplejson.loads(content)
    #pp.pprint(js)
    if showheader:
	print resp
    print js

