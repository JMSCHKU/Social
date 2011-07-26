#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
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
FB_ID = mypass.getFacebookUserId()
ACCESS_TOKEN = fbook_oauth["access_token"]
MAX_LIMIT = 1000

if __name__ == "__main__":
    q = ""
    showheader = False
    csvout = False
    database = True
    fields = ""
    allfields = False
    allowUpdate = False
    limit = MAX_LIMIT
    watch = False
    if len(sys.argv) > 2:
	fbobjtype = sys.argv[1]
	for i in range(2, len(sys.argv)):
	    #print "" + str(i) + " " + sys.argv[i]
	    if sys.argv[i].startswith("-"):
		q = " ".join(sys.argv[2:i])
		break
	    if i == len(sys.argv) - 1:
		q = " ".join(sys.argv[2:len(sys.argv)])
		break
	    '''
	    if q != "":
		q += " "
	    q += str(sys.argv[i])
	    '''
	for j in range(i, len(sys.argv)):
	    #print str(j) + " " + sys.argv[j]
    	    if sys.argv[j] == "-h" or sys.argv[j] == "--http-header":
		showheader = True
	    if sys.argv[j] == "-co" or sys.argv[j] == "--csv-out":
		csvout = True
	    if sys.argv[j] == "-u" or sys.argv[j] == "--update":
		allowUpdate = True
	    if sys.argv[j] == "-no" or sys.argv[j] == "--no-overwrite":
		allowUpdate = False
	    if sys.argv[j] == "-d" or sys.argv[j] == "--database":
		database = True
	    if sys.argv[j] == "-a" or sys.argv[j] == "--all-fields":
		allfields = True
	    if sys.argv[i] == "-w" or sys.argv[i] == "--watch":
		watch = True
	    if sys.argv[j] == "-l":
		if j+1<len(sys.argv):
		    limit = int(sys.argv[j+1])
	    if sys.argv[j].startswith("--limit="):
		limit = int(sys.argv[j].split("=")[1])
    else:
	print usage
	sys.exit()

    # process according to object type
    if allfields:
       	if fbobjtype == "user":
	    fields = "id,name,first_name,last_name,link,locale,updated_time,timezone,gender,verified,third_party_id,location,picture"
	elif fbobjtype == "group":
	    fields = "id,name,feed,members,docs,icon,owner,description,link,privacy,updated_time"
	elif fbobjtype == "event":
	    fields = "id,name,description,feed,attending,picture,venue,owner,privacy,updated_time,start_time,end_time,location"
	elif fbobjtype == "page":
	    fields = "id,name,category,feed,statuses,photos,picture,link,website,username,products,likes,founded,company_overview,mission"
	else:
	    fields = "id,name,feed,members,noreply,maybe,invited,attending,declined,picture,docs" # grab-all fields
	if fbobjtype != "user":
	    limit = min(50, limit)
    else:
       	if fbobjtype == "user":
	    fields = "id,name,first_name,last_name,link,locale,updated_time,timezone,gender,verified,third_party_id,location,picture"
	elif fbobjtype == "group":
	    fields = "id,name,description,picture,updated_time,icon,privacy"
	elif fbobjtype == "event":
	    fields = "id,name,description,picture,updated_time,venue,location,start_time,end_time,privacy,owner"
	elif fbobjtype == "page":
	    fields = "id,name,description,picture,category,link,website,username,products,likes,founded,company_overview,mission"
	elif fbobjtype == "post":
	    fields = "id,name,description,picture,message,link,caption,type,created_time,updated_time,properties,from,to,likes,comments,icon,source,privacy"
	    limit = min(500, limit)
	elif fbobjtype == "application":
	    fields = "id,name,description,picture,link,category"

    # get the parameters
    params = dict()
    params["access_token"] = APP_ID + "|" + ACCESS_TOKEN
    params["metadata"] = 1
    params["fields"] = fields
    params["limit"] = limit
    params["q"] = q
    params["type"] = fbobjtype

    # form the url
    url = "/search?%s" % urllib.urlencode(params)

    # print the url
    if showheader:
	print "https://" + FB_GRAPH_API + url

    # try to connect
    conn = httplib.HTTPSConnection(FB_GRAPH_API, timeout=60)
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
	print r.status, r.reason
	print r.getheaders()

    if r.status != 200:
	sys.exit(sys.exc_info())

    # load the response as json string
    js = json.loads(r.read())

    # Handling of errors returned by the server
    if "error" in js:
	print js["error"]
	sys.exit(sys.exc_info())
    if "error_msg" in js:
	print js["error_msg"]
	sys.exit(sys.exc_info())

    if csvout:
	import csv
	d = datetime.datetime.now()
	cw = csv.writer(open(str(fbidname) + "_" + d.strftime("%Y%m%d%H%M") + ".csv","w"), quoting=csv.QUOTE_MINIMAL)
	if fbobjtype == "group" and (fbconntype == "members" or allfields):
	    if fbconntype is None and allfields:
		members = js["members"]["data"]
	    else:
		members = js["data"]
	    for x in members:
		cw.writerow([x["id"],x["name"].encode("utf8")])
		#print x
    if database:
	if fbobjtype == "user":
	    # minor hack to prevent my friends from being indexed
	    friends_url = "https://graph.facebook.com/me/friends"
	    params_friends = dict()
	    params_friends["access_token"] = APP_ID + "|" + ACCESS_TOKEN
	    params_friends["limit"] = limit
	    friends_url += "?" + urllib.urlencode(params_friends)
	    try:
		conn.request("GET", friends_url)
		#resp, content = conn.request(url, "GET")
	    except Exception:
		print Exception
		print "Couldn't get my friends "
		sys.exit(sys.exc_info())
	    r = conn.getresponse()
	    js_friends = json.loads(r.read())
	    is_my_friend = True
	    for x in js["data"]:
		x['retrieved'] = "NOW()"
		if is_my_friend:
		    is_my_friend = False
		    for y in js_friends["data"]:
			if x["id"] == FB_ID or x["id"] == y["id"]:
			    is_my_friend = True
			    break
		    if is_my_friend:
			continue
		for a in ["name", "first_name", "last_name"]:
		    if a in x and x[a] is not None:
			x[a] = x[a].encode("utf8")
		try:
		    pgconn.insert("facebook_users", x)
		    print str(x["id"]) + "\t" + x["first_name"] + "\t" + x["last_name"]
		except pg.ProgrammingError:
		    try:
			if allowUpdate:
			    print "Cannot insert, will update instead"
			    pgconn.update("facebook_users", x)
		    except pg.ProgrammingError:
			print "Cannot update"
			print x
	if fbobjtype == "group" or fbobjtype == "event" or fbobjtype == "page":
	    for x in js["data"]:
		x['retrieved'] = "NOW()"
		for a in ["name", "description", "location", "icon", "picture", "products", "website", "founded", "company_overview", "mission"]:
		    if a in x and x[a] is not None:
			x[a] = x[a].encode("utf8")
		if "venue" in x:
		    if "city" in x["venue"]:
			x["venue"] = json.dumps(x["venue"]).encode("utf8")
		    else:
			x["venue"] = x["venue"]["street"].encode("utf8")
		if "owner" in x:
		    x["owner"] = x["owner"]["id"]
		if "members" in x:
		    x["members_count"] = len(x["members"])
		table_name = str("facebook_%ss" % fbobjtype)
		try:
		    pgconn.insert(table_name, x)
		    print str(str(x["id"]) + "\t" + x["name"])
		    if watch:
			if fbobjtype == "group":
			    pgconn.query("INSERT INTO facebook_groups_watch (gid, members_count, retrieved) SELECT %(gid)d, COUNT(*), NOW() FROM facebook_users_groups WHERE gid = %(gid)d GROUP BY gid " % {"gid": x["id"]})
			elif fbobjtype == "page":
			    pgconn.insert(table_name + "_watch", {"pid": x["id"], "retrieved": "NOW()", "fan_count": x["fan_count"]})
		except pg.ProgrammingError:
		    try:
			if allowUpdate:
			    print "Cannot insert, will update instead"
			    pgconn.update(table_name, x)
		    except pg.ProgrammingError:
			print "Cannot update"
			print x
	if fbobjtype == "post":
	    for x in js["data"]:
		x['retrieved'] = "NOW()"
		for a in ["name", "description", "location", "icon", "picture", "caption", "message", "link"]:
		    if a in x and x[a] is not None:
			x[a] = x[a].encode("utf8")
		if "from" in x:
		    x["from"] = x["from"]["id"]
		if "to" in x:
		    x["to"] = x["to"]["data"][0]["id"]
		if "properties" in x:
		    x["properties"] = json.dumps(x["properties"]).encode("utf8")
		if "comments" in x:
		    x["comments"] = json.dumps(x["comments"]).encode("utf8")
		if "comments" in x:
		    x["comments_count"] = len(x["comments"])
		table_name = str("facebook_%ss" % fbobjtype)
		try:
		    pgconn.insert(table_name, x)
		    print x["id"]
		except pg.ProgrammingError:
		    try:
			if allowUpdate:
			    print "Cannot insert, will update instead"
			    pgconn.update(table_name, x)
			#print "duplicate: " + x["id"]
		    except pg.ProgrammingError:
			print "Cannot update"
			print x
	if fbobjtype == "application":
	    for x in js["data"]:
		x['retrieved'] = "NOW()"
		for a in ["name", "description", "picture", "link"]:
		    if a in x and x[a] is not None:
			x[a] = x[a].encode("utf8")
		table_name = str("facebook_%ss" % fbobjtype)
		try:
		    pgconn.insert(table_name, x)
		    print str(x["id"])
		except pg.ProgrammingError:
		    try:
			if allowUpdate:
			    print "Cannot insert, will update instead"
			    pgconn.update(table_name, x)
			#print "duplicate: " + x["id"]
		    except pg.ProgrammingError:
			print "Cannot update"
			print x
    else:
	print js
