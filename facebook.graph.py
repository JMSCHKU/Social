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

usage = "usage: facebook.oauth.py [Facebook ID or username] [-h|--http-header|-co|--csv-out|-d|--database\
|-t OBJTYPE|--type=OBJTYPE|-c OBJTYPE|--connection-type=CONNTYPE] "
helptxt = "[OBJTYPE] currently supported: user|group \n\
[CONNTYPE] currently supported: feed|members \n\
Graph API Reference: http://developers.facebook.com/docs/reference/api/ "

pgconn = pg.DB('YOUR_DB', '127.0.0.1', 5432, None, None, 'YOUR_USERNAME', 'YOUR_PASSWORD')

FB_GRAPH_API = "graph.facebook.com"
APP_ID = "(a long digit-only string)"
ACCESS_TOKEN = "(some key that's always the same for a given user)-(your user id)|(some funky key that changes)"

fbid = 0
fbname = ""
showheader = False
csvout = False
database = False
allfields = False
fields = ""
fbobjtype = None
fbconntype = None

if len(sys.argv) > 1:
    if sys.argv[1] == "?" or sys.argv[1] == "--help":
	print helptxt
	sys.exit()
    try:
	fbid = int(sys.argv[1])
    except ValueError: # fall back to unique name
	fbid = 0
	fbname = sys.argv[1]
else:
    print usage
    sys.exit()

if re.search('^[\w.]+$', fbname) is not None:
    fbidname = fbname
elif fbid > 0:
    fbidname = fbid
else:
    print usage
    sys.exit()

if len(sys.argv) > 2:
    for i in range(2,len(sys.argv)):
	if sys.argv[i] == "-h" or sys.argv[i] == "--http-header":
    	    showheader = True
	if sys.argv[i] == "-co" or sys.argv[i] == "--csv-out":
	    csvout = True
	if sys.argv[i] == "-d" or sys.argv[i] == "--database":
	    database = True
	if sys.argv[i] == "-af" or sys.argv[i] == "--all-fields":
	    allfields = True
	if sys.argv[i] == "-t":
	    if i+1<len(sys.argv):
		fbobjtype = sys.argv[i+1]
	if sys.argv[i].startswith("--type="):
	    fbobjtype = sys.argv[i].split("=")[1]
	if sys.argv[i] == "-c":
	    if i+1<len(sys.argv):
		fbconntype = sys.argv[i+1]
	if sys.argv[i].startswith("--connection="):
	    fbconntype = sys.argv[i].split("=")[1]

# process according to object type
if fbobjtype == "user":
    if allfields:
	fields = "id,name,first_name,last_name,link,locale,updated_time,timezone,gender,verified,third_party_id,location"

# get the parameters
params = dict()
params['access_token'] = APP_ID + "|" + ACCESS_TOKEN
params['fields'] = fields

# form the url
url = "/" + str(fbidname)
if fbconntype is not None:
    url += "/" + fbconntype
url += "?%s" % urllib.urlencode(params)

# try to connect
conn = httplib.HTTPSConnection(FB_GRAPH_API)
try:
    conn.request("GET", url)
    #resp, content = conn.request(url, "GET")
except Exception:
    sys.exit(sys.exc_info())

# get the response
r = conn.getresponse()

# print status code and headers
if showheader:
    print r.status, r.reason
    print r.getheaders()

# load the response as json string
js = json.loads(r.read())

if csvout:
    import csv
    d = datetime.datetime.now()
    cw = csv.writer(open(str(fbidname) + "_" + d.strftime("%Y%m%d%H%M") + ".csv","w"), quoting=csv.QUOTE_MINIMAL)
    if fbobjtype == "group" and fbconntype == "members":
	for x in js["data"]:
	    cw.writerow([x["id"],x["name"].encode("utf8")])
	    #print x
if database:
    if fbobjtype == "group" and fbconntype == "members":
	d = datetime.datetime.now()
	for x in js["data"]:
	    x["name"] = x["name"].encode("utf8")
	    try:
		pgconn.insert("facebook_users", x)
		pgconn.insert("facebook_users_groups", {"uid":long(x["id"]),"gid":long(fbid)})
	    except pg.ProgrammingError, ValueError:
		continue
	    #print x
else:
    print js

