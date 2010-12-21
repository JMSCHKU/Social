#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sinastorage.py stores data retrieved using sinagetter.sh into a database (see sinaweibo.sql)

import sys
import pg
import mypass
import simplejson
import time
import datetime
import string
import types

import mypass

usage = "sinastorage.py [option::1=user_timeline,2=users,3=friends,4=followers] [name of file to insert in DB] [user_id for friends/followers (source_id)]"
table_name = "sinaweibo"

pgconn = mypass.getConn()

doupdate = False
justretweets = False
sleeptime = 600

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

f = open(fname, "r")
content = f.read()
js = simplejson.loads(content)
r = dict()

if opt == 1:
    if not isinstance(js, types.ListType):
	js = [js]
    if len(js) <= 0:
	print js
	sys.exit()
    if "error" in js[0]:
	print js[0]["error"]
	time.sleep(sleeptime)
	sys.exit()
    for j in range(len(js)):
	l = js[j]
	last_tweet = l
	row = None
	keys = l.keys()
	#if l["in_reply_to_user_id"] is not None and type(l["in_reply_to_user_id"]) is types.StringType and len(l["in_reply_to_user_id"]) == 2:
	#    l["in_reply_to_user_id"] = None
	r = {"id": l["id"], "created_at": l["created_at"], "text": l["text"].encode("utf8"), "in_reply_to_user_id": l["in_reply_to_user_id"],\
	    "in_reply_to_status_id": l["in_reply_to_status_id"], "source": l["source"].encode("utf8")}
	if "retweeted_status" in keys and l["retweeted_status"] is not None:
	    r["retweeted_status"] = l["retweeted_status"]["id"]
	else:
	    if justretweets:
		continue
	if "user" in l:
	    if l["user"]["domain"] is not None:
		r["screen_name"] = l["user"]["domain"]
	    elif l["user"]["screen_name"] is not None:
		r["screen_name"] = l["user"]["screen_name"].encode("utf8")
	    else:
		r["screen_name"] = None
	else:
	    r["screen_name"] = None
	if l["user"] is not None:
	    r["user_id"] = l["user"]["id"]
	if "thumbnail_pic" in keys:
	    r["thumbnail_pic"] = l["thumbnail_pic"].encode("utf8")
	if "bmiddle_pic" in keys:
	    r["bmiddle_pic"] = l["bmiddle_pic"].encode("utf8")
	if "original_pic" in keys:
	    r["original_pic"] = l["original_pic"].encode("utf8")
	try:
	    row = pgconn.insert(table_name, r)
	except pg.ProgrammingError, pg.InternalError:
	    try:
		if doupdate:
		    row = pgconn.update(table_name, r)
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
elif opt == 2:
    table_name += "_users"
    if not isinstance(js, types.ListType):
	js = [js]
    if len(js) <= 0:
	print js
	sys.exit()
    if "error" in js[0]:
	print js[0]["error"]
	time.sleep(sleeptime)
	sys.exit()
    for l in js:
	if fromstatuses and "user" in l:
	    l = l["user"]
    	r = {"id": l["id"], "name": l["name"].encode("utf8"), "screen_name": l["screen_name"].encode("utf8"),\
	"province": l["province"], "city": l["city"],"location": l["location"].encode("utf8"),\
	"description": l["description"].encode("utf8"), "profile_image_url": l["profile_image_url"].encode("utf8"),\
	"url": l["url"].encode("utf8"),"domain": l["domain"], "gender": l["gender"], "followers_count": l["followers_count"],\
	"friends_count": l["friends_count"],"created_at": l["created_at"], "favourites_count": l["favourites_count"],\
	"allow_all_act_msg": l["allow_all_act_msg"],"geo_enabled": l["geo_enabled"],
	"verified": l["verified"], "statuses_count": l["statuses_count"],
	"retrieved": "NOW()"}
	try:
	    pgconn.insert(table_name, r)
	except pg.ProgrammingError, pg.InternalError:
	    print "user duplicate found in DB..."
	    try:
		if doupdate:
		    print "trying to update instead"
		    pgconn.update(table_name, r)
	    except:
		print "an error has occurred (row cannot be updated)"
	    print r
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

f.close()
