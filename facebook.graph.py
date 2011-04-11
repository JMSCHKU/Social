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
import json

import mypass

usage = "usage: facebook.oauth.py [Facebook ID or username] [-h|--http-header|-co|--csv-out|-d|--database\
|-t OBJTYPE|--type=OBJTYPE|-c OBJTYPE|--connection-type=CONNTYPE] "
helptxt = "[OBJTYPE] currently supported: user|group \n\
[CONNTYPE] currently supported: feed|members \n\
Graph API Reference: http://developers.facebook.com/docs/reference/api/ "

pgconn = mypass.getConn()

FB_GRAPH_API = "graph.facebook.com"
fbook_oauth = mypass.getFacebookOauth()
APP_ID = str(fbook_oauth["app_id"])
ACCESS_TOKEN = fbook_oauth["access_token"]
FBPOST_TYPES = ["video", "link", "status", "photo", "music"]

def getMetadata(fbid, showHeaders=False):
    params = dict()
    params['access_token'] = APP_ID + "|" + ACCESS_TOKEN
    params['metadata'] = 1
    url = fbid + "?" + urllib.urlencode(params)
    conn = httplib.HTTPSConnection(FB_GRAPH_API)
    try:
	conn.request("GET", url)
    except Exception:
	#sys.exit(sys.exc_info())
	return json.loads('{}')
    r = conn.getresponse()
    if showHeaders:
	print "https://" + FB_GRAPH_API + url
	print r.status, r.reason
	print r.getheaders()
    js = json.loads(r.read())
    return js

def fb_comments_likes(fbpostid, comments=list(), likes=list()):
    #print "postid for comments likes: " + str(fbpostid)
    #row = {"id": fbpostid}
    for x in comments:
	x["from"] = x["from"]["id"]
	x["message"] = x["message"].encode("utf8")
	x["pid"] = fbpostid
	try:
	    pgconn.insert("facebook_comments", x)
	except pg.ProgrammingError:
	    continue
    for x in likes:
	x["uid"] = x["id"]
	x["pid"] = fbpostid
	try:
	    pgconn.insert("facebook_likes", x)
	except pg.ProgrammingError:
	    continue
    if len(comments) > 0 and len(likes) > 0:
	pgconn.query("UPDATE facebook_posts SET comments_count = %(comments)d, likes = %(likes)d WHERE id = '%(id)s' " % {"comments": len(comments), "likes": len(likes), "id": fbpostid})
	#print len(comments) + " comments & " + str(len(likes)) + " likes"
    elif len(comments) > 0:
	pgconn.query("UPDATE facebook_posts SET comments_count = %(comments)d WHERE id = '%(id)s' " % {"comments": len(comments), "id": fbpostid})
	#print len(comments) + " comments"
    elif len(likes) > 0:
	pgconn.query("UPDATE facebook_posts SET likes = %(likes)d WHERE id = '%(id)s' " % {"likes": len(likes), "id": fbpostid})
	#print str(len(likes)) + " likes"

if __name__ == "__main__":
    fbid = 0
    fbname = ""
    showheader = False
    csvout = False
    database = True
    allfields = False
    fields = ""
    fbobjtype = None
    fbconntype = None
    allowUpdate = False
    quiet = False
    watch = False
    is_new_insert = False

    if len(sys.argv) > 1:
	if sys.argv[1] == "?" or sys.argv[1] == "--help":
	    print helptxt
	    sys.exit()
	try:
	    fbid = long(sys.argv[1])
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
	    if sys.argv[i] == "-no" or sys.argv[i] == "--no-overwrite":
		allowUpdate = False
	    if sys.argv[i] == "-u" or sys.argv[i] == "--update":
		allowUpdate = True
	    if sys.argv[i] == "-d" or sys.argv[i] == "--database":
		database = True
	    if sys.argv[i] == "-a" or sys.argv[i] == "--all-fields":
		allfields = True
	    if sys.argv[i] == "-q" or sys.argv[i] == "--quiet":
		quiet = True
	    if sys.argv[i] == "-w" or sys.argv[i] == "--watch":
		watch = True
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

    #metadata = getMetadata(fbidname)
    #if fbobjtype is None:
    #	fbobjtype = metadata["type"]

    # process according to object type
    if allfields:
       	if fbobjtype == "user":
	    fields = "id,name,first_name,last_name,link,locale,updated_time,timezone,gender,verified,third_party_id,location"
	elif fbobjtype == "group":
	    fields = "id,name,feed,members,docs,icon,owner,description,link,privacy,updated_time"
	    #fields = "feed,members,docs"
	elif fbobjtype == "event":
	    fields = "id,name,description,feed,attending,declined,maybe,noreply,invited,venue,owner,privacy,updated_time,start_time,end_time,location"
	    #fields = "feed,noreply,maybe,invited,attending,declined,picture"
	elif fbobjtype == "page":
	    fields = "id,name,category,feed,statuses,photos,link,website,username,products,likes,founded,company_overview,mission"
	    #fields = "id,name,description,picture,category,link,website,username,products,fan_count,founded,company_overview,mission"
	elif fbobjtype == "application":
	    fields = "id,name,description,link,category"
	elif fbobjtype == "post":
	    fields = "id,name,description,message,link,caption,type,created_time,updated_time,properties,from,to,likes,comments,icon,source,privacy"
	elif fbobjtype in FBPOST_TYPES:
	    fields = "id,likes,comments"
	else:
	    fields = ""#feed,members,noreply,maybe,invited,attending,declined,picture,docs" # grab-all fields

    # get the parameters
    params = dict()
    params['access_token'] = APP_ID + "|" + ACCESS_TOKEN
    params['fields'] = fields
    params['metadata'] = 1
    params['type'] = fbobjtype
    if fbobjtype in FBPOST_TYPES:
	params['type'] = "post"

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
    try:
	r = conn.getresponse()
    except Exception:
	print "https://" + FB_GRAPH_API + url
	sys.exit(sys.exc_info())

    # print status code and headers
    if showheader:
	print "https://" + FB_GRAPH_API + url
	print r.status, r.reason
	print r.getheaders()

    # load the response as json string
    js = json.loads(r.read())

    # Handling of errors returned by the server
    if not js:
	print js
	sys.exit(sys.exc_info())
    if "error" in js:
	print js["error"]
	sys.exit(sys.exc_info())
    if "error_msg" in js:
	print js["error_msg"]
	sys.exit(sys.exc_info())


    # break if the reflected type does not match the one specified
    if fbobjtype is None:
	fbobjtype = js["type"]
    if "type" in js and js["type"] != fbobjtype and not js["type"] in FBPOST_TYPES:
	print "Specified type (%(stype)s) does not match reflected one [real type:%(rtype)s] " % { "stype": fbobjtype, "rtype": js["type"]}
	sys.exit()
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
	if fbobjtype == "post" or fbobjtype in FBPOST_TYPES and (fbconntype == "comments" or fbconntype == "likes" or allfields):
	    comments = list()
	    likes = list()
	    if fbconntype is None and allfields:
		comments = js["comments"]["data"]
		likes = js["likes"]["data"]
	    elif fbconntype == "comments":
    		comments = js["data"]
	    elif fbconntype == "likes":
		likes = js["data"]
	    cwc = csv.writer(open(str(fbidname) + "_" + d.strftime("%Y%m%d%H%M") + "_comments.csv","w"), quoting=csv.QUOTE_MINIMAL)
	    for x in comments:
		print x["message"]
		print x["from"]["name"]
		print x["id"]
		cwc.writerow([x["id"],x["from"]["id"],x["from"]["name"].encode("utf8"),x["message"].encode("utf8"),x["created_time"]])
	    cwl = csv.writer(open(str(fbidname) + "_" + d.strftime("%Y%m%d%H%M") + "_likes.csv","w"), quoting=csv.QUOTE_MINIMAL)
	    for x in likes:
		cwl.writerow([x["id"],x["name"].encode("utf8")])
	    #print comments
	    #print likes
    if database:
	if fbobjtype == "user":
	    js['retrieved'] = "NOW()"
	    for a in ["name", "first_name", "last_name"]:
		if a in js and js[a] is not None:
		    js[a] = js[a].encode("utf8")
	    try:
		pgconn.insert("facebook_users", js)
		if showheader:
		    print str(js["id"]) + "\t" + js["first_name"] + "\t" + js["last_name"]
	    except pg.ProgrammingError:
		try:
		    if allowUpdate:
			pgconn.update("facebook_users", js)
		except pg.ProgrammingError:
		    if not quiet:
			print "Cannot update"
		    print js
	if fbobjtype == "page":
	    js['retrieved'] = "NOW()"
	    if "location" in js:
		js["location"] = json.dumps(js["location"])
	    for a in ["name", "description", "location", "icon", "picture", "products", "website", "founded", "company_overview", "mission"]:
		if a in js and js[a] is not None:
		    js[a] = js[a].encode("utf8")
	    if "fan_count" in js:
		js["likes"] = js["fan_count"]
	    elif "likes" in js:
		js["fan_count"] = js["likes"]
	    else:
		js["likes"] = 0
	    if "likes" in js:
		js["fan_count"] = js["likes"]
	    table_name = str("facebook_%ss" % fbobjtype)
	    try:
		pgconn.insert(table_name, js)
		if watch:
		    pgconn.insert(table_name + "_watch", {"pid": js["id"], "retrieved": "NOW()", "fan_count": js["likes"]})
	    except pg.ProgrammingError:
		try:
		    if allowUpdate:
			if not quiet:
			    print "Cannot insert, will update instead"
			pgconn.update(table_name, js)
		except pg.ProgrammingError:
		    print "Cannot update"
		    print js
	if fbobjtype == "application":
	    js['retrieved'] = "NOW()"
	    for a in ["name", "description", "picture", "link"]:
		if a in js and js[a] is not None:
		    js[a] = js[a].encode("utf8")
	    table_name = str("facebook_%ss" % fbobjtype)
	    try:
		pgconn.insert(table_name, js)
		print str(str(js["id"]))
	    except pg.ProgrammingError:
		try:
		    if allowUpdate:
			if not quiet:
			    print "Cannot insert, will update instead"
			pgconn.update(table_name, js)
		    #print "duplicate: " + js["id"]
		except pg.ProgrammingError:
		    if not quiet:
			print "Cannot update"
		    print js
	if fbobjtype == "group" or fbobjtype == "event":
	    js['retrieved'] = "NOW()"
    	    for x in ["name", "description", "location", "icon", "picture", "link"]:
		if x in js and js[x] is not None:
		    js[x] = js[x].encode("utf8")
	    #if "members" in js:
		#sql_members = "SELECT COUNT(*) AS members_count FROM facebook_groups g LEFT JOIN facebook_users_groups ug ON g.id = ug.gid WHERE g.id = %d " % fbid
		#res_members = pgconn.query(sql_members).getresult()
		#js["members_count"] = res_members[0][0]
	    if "venue" in js:
		js["venue"] = json.dumps(js["venue"]).encode("utf8")
	    if "owner" in js:
		js["owner"] = js["owner"]["id"]
	    table_name = str("facebook_%ss" % fbobjtype)
	    try:
		pgconn.insert(table_name, js)
		if showheader:
		    print str(js["id"]) + "\t" + js["name"]
		is_new_insert = True
	    except pg.ProgrammingError:
		try:
		    if allowUpdate:
			if not quiet:
			    print "Cannot insert, will update instead"
			pgconn.update(table_name, js)
		except pg.ProgrammingError:
		    if not quiet:
			print "Cannot update"
		    print js
	if (fbobjtype == "group" and (fbconntype == "members" or allfields)) or (fbobjtype == "event" and (fbconntype == "attending" or allfields)):
	    d = datetime.datetime.now()
	    if allfields:
		if fbobjtype == "group":
		    members = js["members"]["data"]
		elif fbobjtype == "event":
		    members = list()
		    if "invited" in js:
			members += js["invited"]["data"]
		    if "attending" in js:
			members += js["attending"]["data"]
		    if "declined" in js:
			members += js["declined"]["data"]
		    if "noreply" in js:
			members += js["noreply"]["data"]
		    if "maybe" in js:
			members += js["maybe"]["data"]
	    else:
		members = js["data"]
	    print "len(members): " + str(len(members))
	    for x in members:
		x["name"] = x["name"].encode("utf8")
		try:
		    pgconn.insert("facebook_users", x)
		    if showheader:
			print str(x["id"]) + "\t" + x["name"]
		except pg.ProgrammingError:
		    try:
			if allowUpdate:
			    if not quiet:
				print "Cannot insert, will update instead"
			    pgconn.update("facebook_users", x)
		    except pg.ProgrammingError:
			if not quiet:
			    print "Cannot update"
		if fbobjtype == "group":
		    try:
			pgconn.insert("facebook_users_groups", {"uid":long(x["id"]),"gid":long(fbid)})
			if showheader:
			    print "members: " + str(x["id"]) + "\t" + str(fbid)
		    except pg.ProgrammingError:
			pass
		elif fbobjtype == "event":
		    if "rsvp_status" in x:
			try:
			    pgconn.insert("facebook_users_events", {"uid":long(x["id"]),"eid":long(fbid),"rsvp_status":x["rsvp_status"], "retrieved": "NOW()"})
			except pg.ProgrammingError:
			    pgconn.update("facebook_users_events", {"uid":long(x["id"]),"eid":long(fbid),"rsvp_status":x["rsvp_status"], "retrieved": "NOW()"})
			if showheader:
			    print "event: " + str(x["id"]) + "\t" + str(fbid) + "\t" + x["rsvp_status"]
		    else:
			pgconn.insert("facebook_users_events", {"uid":long(x["id"]),"eid":long(fbid), "retrieved": "NOW()"})
			if showheader:
			    print "event: " + str(x["id"]) + "\t" + str(fbid)
		#print x
		
	    if fbobjtype == "group":
	       	sql_members = "SELECT COUNT(*) AS members_count FROM facebook_groups g LEFT JOIN facebook_users_groups ug ON g.id = ug.gid WHERE g.id = %d " % fbid
		res_members = pgconn.query(sql_members).getresult()
		pgconn.query("UPDATE facebook_groups g SET members_count = %(members)d WHERE g.id = %(id)d " % { "members": res_members[0][0], "id": fbid })

	    if watch and is_new_insert:
		if pgobtype == "group":
		    pgconn.query("INSERT INTO facebook_groups_watch (gid, members_count, retrieved) SELECT %(gid)d, COUNT(*), NOW() FROM facebook_users_groups WHERE gid = %(gid)d GROUP BY gid " % {"gid": long(fbid)})
		elif pgobjtype == "event":
		    sql_event_watch = "SELECT rsvp_status, COUNT(*) as count FROM facebook_users_events WHERE eid = %(eid)d GROUP BY rsvp_status ORDER BY rsvp_status " % {"eid": long(fbid)}
		    resew = pgconn.query(sql_event_watch).dictresult()
		    ew_attending = ew_declined = ew_not_replied = ew_unsure = 0
		    for x in resew:
			if x["rsvp_status"] == "attending":
			    ew_attending = x["count"]
			elif x["rsvp_status"] == "declined":
			    ew_declined = x["count"]
			elif x["rsvp_status"] == "not_replied":
			    ew_not_replied = x["count"]
			elif x["rsvp_status"] == "unsure":
			    ew_unsure = x["count"]
		    #sql_event_watch_ins = "INSERT INTO facebook_events_watch (eid, attending_count, declined_count, notreplied_count, unsure_count, retrieved) VALUES (%(eid)d, %(attending)d, %(declined)d, %(not_replied)d, %(unsure)d, NOW()) " \
		    #% {"attending": ew_attending, "declined": ew_declined, "not_replied": ew_not_replied, "unsure": ew_unsure}
		    #pgconn.query(sql_event_watch_ins)
		    pgconn.insert("facebook_events_watch", {"eid": long(fbid), "attending_count": ew_attending, "declined_count": ew_declined, "notreplied_count": ew_not_replied, "unsure_count": ew_unsure, "retrieved": "NOW()"})
	if fbobjtype in FBPOST_TYPES and (allfields or fbconntype == "likes" or fbconntype == "comments"):
	    comments = list()
	    likes = list()
	    if fbconntype is None and allfields:
		comments = js["comments"]["data"]
		likes = js["likes"]["data"]
	    elif fbconntype == "comments":
    		comments = js["data"]
	    elif fbconntype == "likes":
		likes = js["data"]
	    fb_comments_likes(fbname, comments, likes)
	if ",feed," in fields and "feed" in js:
	    if allfields:
		feed = js["feed"]["data"]
	    elif fbconntype == "feed":
		feed = js["data"]
	    for x in feed:
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
		comments = list()
		likes = list()
		if "comments" in x:
		    if "count" in x["comments"]:
			x["comments_count"] = x["comments"]["count"]
		    if "data" in x["comments"]:
			comments = x["comments"]["data"]
		fb_comments_likes(x["id"], comments, likes)
		if "comments" in x:
		    x["comments"] = json.dumps(x["comments"]).encode("utf8")
		try:
		    pgconn.insert("facebook_posts", x)
		    print "add post: " + str(x["id"])
		except pg.ProgrammingError:
		    try:
			if allowUpdate:
			    if not quiet:
				print "Cannot insert, will update instead"
			    pgconn.update("facebook_posts", x)
			#print "duplicate: " + x["id"]
		    except pg.ProgrammingError:
			if not quiet:
			    print "Cannot update"
			print x
    else:
	print js

