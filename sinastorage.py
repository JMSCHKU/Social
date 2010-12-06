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

pgconn = pg.DB('YOUR_DB', '127.0.0.1', 5432, None, None, 'YOUR_USERNAME', 'YOUR_PASSWORD')

usage = "sinastorage.py [option::1=user_timeline,2=users,3=friends,4=followers] [name of file to insert in DB] [user_id for friends/followers (source_id)]"
table_name = "sinaweibo"

if len(sys.argv) > 2:
    try:
	opt = int(sys.argv[1])
	fname = str(sys.argv[2])
    except ValueError:
	print usage
	sys.exit()
if opt >= 3 and opt <= 4:
    try:
	user_id = int(sys.argv[3])
    except ValueError:
	print usage
	sys.exit()

f = open(fname, "r")
content = f.read()
js = simplejson.loads(content)
r = dict()

if opt == 1:
    for j in range(len(js)):
	l = js[j]
	last_tweet = l
	if l["in_reply_to_user_id"] != None and type(l["in_reply_to_user_id"]) is types.StringType and len(l["in_reply_to_user_id"]) == 2:
	    l["in_reply_to_user_id"] = None
	r = {"id": l["id"], "created_at": l["created_at"], "text": l["text"].encode("utf8"), "in_reply_to_user_id": l["in_reply_to_user_id"],\
	    "in_reply_to_status_id": l["in_reply_to_status_id"]}
	if l["user"]["domain"] is not None:
	    r["screen_name"] = l["user"]["domain"]
	elif l["user"]["screen_name"] is not None:
	    r["screen_name"] = l["user"]["screen_name"]
	else:
	    r["screen_name"] = string.split(fname, "-")[0]
	if l["user"] is not None:
	    r["user_id"] = l["user"]["id"]
	try:
	    pgconn.insert(table_name, r)
	except pg.ProgrammingError, pg.InternalError:
	    print last_tweet
	    print "tweets up to date (duplicate found in DB)"
	    #break
elif opt == 2:
    table_name += "_users"
    l = js
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
    	print "user duplicate found in DB... trying to update instead"
	try:
	    pgconn.update(table_name, r, {"id": l["id"]})
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
	    print r
	    print "duplicate"

f.close()
