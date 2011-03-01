#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sinastorage.py stores data retrieved using sinagetter.sh into a database (see sinaweibo.sql)

import sys
import pg
import simplejson
import time
import datetime
import string
import types

import mypass

usage = "sinastorage.py [option::1=user_timeline,2=users,3=friends,4=followers] [name of file to insert in DB] [user_id for friends/followers (source_id)]"
table_name = "sinaweibo"

pgconn = mypass.getConn()

tobeginning = True
last_one = ""
insert_user = False
doupdate = False
justretweets = False
sleeptime = 300

if len(sys.argv) > 2:
    try:
	opt = int(sys.argv[1])
	fname = str(sys.argv[2])
    except ValueError:
	print usage
	sys.exit()
else:
    print usage
    sys.exit()

if opt >= 3 and opt <= 4:
    try:
	user_id = int(sys.argv[3])
    except ValueError:
	print usage
	sys.exit()
elif opt <= 2:
    fromstatuses = False
    for i in range(3,len(sys.argv)):
	if sys.argv[i] == "-u" or sys.argv[i] == "--update":
	    doupdate = True
	if sys.argv[i] == "-rt" or sys.argv[i] == "--retweets":
	    justretweets = True
	if sys.argv[i] == "-s" or sys.argv[i] == "--from-statuses":
	    fromstatuses = True
elif opt == 8:
    for i in range(3,len(sys.argv)):
	if sys.argv[i] == "-b" or sys.argv[i] == "--to-beginning":
	    tobeginning = True
	if sys.argv[i] == "-nd" or sys.argv[i] == "--no-duplicates":
	    tobeginning = False
	if sys.argv[i] == "-U" or sys.argv[i] == "--user":
	    insert_user = True

f = open(fname, "r")
content = f.read()
js = simplejson.loads(content)
r = dict()

# in case of error, exit
if content != "[]" and "error" in js[0]:
    print js[0]["error"]
    if js[0]["error"].startswith("40302"):
	sys.exit()
    if js[0]["error"].startswith("40023"):
	sys.exit()
    if js[0]["error"].startswith("40031"):
	sys.exit()
    time.sleep(sleeptime)
    sys.exit()

if opt == 1:
    if not isinstance(js, types.ListType):
	js = [js]
    if len(js) <= 0:
	print js
	sys.exit()
    for j in range(len(js)):
	l = js[j]
	last_tweet = l
	row = None
	#if l["in_reply_to_user_id"] is not None and type(l["in_reply_to_user_id"]) is types.StringType and len(l["in_reply_to_user_id"]) == 2:
	#    l["in_reply_to_user_id"] = None
	for a in ["text", "source", "thumbnail_pic", "bmiddle_pic", "original_pic"]:
	    if a in l and l[a] is not None:
		l[a] = l[a].encode("utf8")
	if "retweeted_status" in l and l["retweeted_status"] is not None:
	    l["retweeted_status"] = l["retweeted_status"]["id"]
	else:
	    if justretweets:
		continue
	if "user" in l:
	    if l["user"]["name"] is not None:
		l["screen_name"] = l["user"]["name"].encode("utf8")
	    elif l["user"]["screen_name"] is not None:
		l["screen_name"] = l["user"]["screen_name"].encode("utf8")
	    elif l["user"]["domain"] is not None:
		l["screen_name"] = l["user"]["domain"]
	    else:
		l["screen_name"] = None
	else:
	    l["screen_name"] = None
	if l["user"] is not None:
	    l["user_id"] = l["user"]["id"]
	try:
	    row = pgconn.insert(table_name, l)
	except pg.ProgrammingError, pg.InternalError:
	    try:
		if doupdate:
		    row = pgconn.update(table_name, l)
		    print "updating..."
		    print row
	    except:
		print "can't insert or update"
		print last_tweet
	    #pass
	if row is not None and l["geo"] is not None:
	    if "type" in l["geo"] and l["geo"]["type"] == "Point" and "coordinates" in l["geo"] and l["geo"]["coordinates"] is not None and len(l["geo"]["coordinates"]) == 2:
		lat = l["geo"]["coordinates"][0]
		lng = l["geo"]["coordinates"][1]
		wkt_point = "POINT(" + str(lat) + " " + str(lng) + ")"
		sql = "UPDATE %(table_name)s SET geo = ST_GeomFromText('%(wkt_point)s', 4326) WHERE id = %(id)d " % {"table_name": table_name, "wkt_point": wkt_point, "id": row["id"]}
		try:
		    pgconn.query(sql)
		except:
		    print sql
		    print "geo error: " + wkt_point
	    #print last_tweet
	    #print "tweets up to date (duplicate found in DB)"
	    #break
	# try to add the user
	if insert_user and "user" in l:
	    u = l["user"]
	    u["retrieved"] = "NOW()"
	    for a in ["name", "screen_name", "location", "description", "profile_image_url", "url"]:
		if a in u and u[a] is not None:
		    u[a] = u[a].encode("utf8")
	    try:
		pgconn.insert("sinaweibo_users", u)
	    except pg.ProgrammingError, pg.InternalError:
		try:
		    if doupdate:
			print "user: trying to update instead"
			pgconn.update("sinaweibo_users", u)
		except:
		    print "user: an error has occurred (row cannot be updated)"
		print u
elif opt == 2:
    table_name += "_users"
    if not isinstance(js, types.ListType):
	js = [js]
    if len(js) <= 0:
	print js
	sys.exit()
    for l in js:
	l["retrieved"] = "NOW()"
	if fromstatuses and "user" in l:
	    l = l["user"]
	for a in ["name", "screen_name", "location", "description", "profile_image_url", "url"]:
	    if a in l and l[a] is not None:
		l[a] = l[a].encode("utf8")
	'''
    	r = {"id": l["id"], "name": l["name"].encode("utf8"), "screen_name": l["screen_name"].encode("utf8"),\
	"province": l["province"], "city": l["city"],"location": l["location"].encode("utf8"),\
	"description": l["description"].encode("utf8"), "profile_image_url": l["profile_image_url"].encode("utf8"),\
	"url": l["url"].encode("utf8"),"domain": l["domain"], "gender": l["gender"], "followers_count": l["followers_count"],\
	"friends_count": l["friends_count"],"created_at": l["created_at"], "favourites_count": l["favourites_count"],\
	"allow_all_act_msg": l["allow_all_act_msg"],"geo_enabled": l["geo_enabled"],
	"verified": l["verified"], "statuses_count": l["statuses_count"],
	"retrieved": "NOW()"}
	'''
	try:
	    pgconn.insert(table_name, l)
	except pg.ProgrammingError, pg.InternalError:
	    print "user duplicate found in DB..."
	    try:
		if doupdate:
		    print "trying to update instead"
		    pgconn.update(table_name, l)
	    except:
		print "an error has occurred (row cannot be updated)"
	    print l
elif opt == 3 or opt == 4:
    if opt == 3:
	table_name += "_friends"
    elif opt == 4:
	table_name += "_followers"
    l = js["ids"]
    for x in l:
	r = {"source_id": user_id, "target_id": x}
	r["retrieved"] = "NOW()"
	try:
	    pgconn.insert(table_name, r)
	except pg.ProgrammingError, pg.InternalError:
	    #print "duplicate and cannot update"
	    try:
		pgconn.update(table_name, r)
	    except:
		print r
		print "duplicate and cannot update"
elif opt == 8:
    table_name += "_comments"
    for x in js:
	last_one = x
	for a in ["text"]:
    	    if a in x and x[a] is not None:
		x[a] = x[a].encode("utf8")
	if "user" in x:
	    x["user_id"] = x["user"]["id"]
	else:
	    u = None
	if "status" in x:
	    x["status_id"] = x["status"]["id"]
	try:
	    pgconn.insert(table_name, x)
	except pg.ProgrammingError, pg.InternalError:
	    if not tobeginning:
		print last_one
	       	print "UP-TO-DATE: comments up to date (duplicate found in DB)"
		break
	    try:
		if doupdate:
		    print "trying to update instead"
		    pgconn.update(table_name, x)
	    except:
		print "an error has occurred (row cannot be updated)"
	    print x
	# try to add the user
	if insert_user and "user" in x:
	    u = x["user"]
	    u["retrieved"] = "NOW()"
	    for a in ["name", "screen_name", "location", "description", "profile_image_url", "url"]:
		if a in u and u[a] is not None:
		    u[a] = u[a].encode("utf8")
	    try:
		pgconn.insert("sinaweibo_users", u)
	    except pg.ProgrammingError, pg.InternalError:
		try:
		    if doupdate:
			print "user: trying to update instead"
			pgconn.update("sinaweibo_users", u)
		except:
		    print "user: an error has occurred (row cannot be updated)"
		print u

f.close()
