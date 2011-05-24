#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Not used anymore. Superseded by sinaweibo.oauth.py

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

tobeginning = False
tobeginning_grace = 190
last_one = ""
insert_user = False
doupdate = False
doupdate_user = False
justretweets = False
verbose = False
sleeptime = 150
breakafterupdate = False

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
	if sys.argv[i] == "-b" or sys.argv[i] == "--to-beginning":
	    tobeginning = True
	if sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
	    verbose = True
	if sys.argv[i] == "-q" or sys.argv[i] == "--quiet":
	    verbose = False
	if sys.argv[i] == "-u" or sys.argv[i] == "--update":
	    doupdate = True
	if sys.argv[i] == "-rt" or sys.argv[i] == "--retweets":
	    justretweets = True
	if sys.argv[i] == "-s" or sys.argv[i] == "--from-statuses":
	    fromstatuses = True
	if sys.argv[i] == "-U" or sys.argv[i] == "--user":
	    insert_user = True
	if sys.argv[i] == "-Uu" or sys.argv[i] == "--update-user":
	    doupdate_user = True
elif opt == 7 or opt == 8:
    for i in range(3,len(sys.argv)):
	if sys.argv[i] == "-b" or sys.argv[i] == "--to-beginning":
	    tobeginning = True
	if sys.argv[i] == "-nd" or sys.argv[i] == "--no-duplicates":
	    tobeginning = False
	if sys.argv[i] == "-U" or sys.argv[i] == "--user":
	    insert_user = True

f = open(fname, "r")
content = f.read()
try:
    js = simplejson.loads(content)
except ValueError:
    print "JSON ERROR: " + fname + "\t" + content
    sys.exit()
r = dict()

# in case of error, exit
if content != "[]" and ((len(js) > 0 and 0 in js) or "error" in js):
    if len(js) > 0 and 0 in js and "error" in js[0]:
	errorJs = js[0]["error"]
    elif "error" in js:
	errorJs = js["error"]
    else:
	errorJs = None
    if errorJs is not None:
	if verbose:
	    print "FAILURE"
	print errorJs
	if errorJs.startswith("40302"):
	    sys.exit()
	if errorJs.startswith("40023"):
	    sys.exit()
	if errorJs.startswith("40031"):
	    sys.exit()
	time.sleep(sleeptime)
	sys.exit()

if opt == 1 or opt == 7:
    if not isinstance(js, types.ListType):
	js = [js]
    if len(js) <= 0:
	print js
	sys.exit()
    for j in range(len(js)):
	l = js[j]
	last_tweet = l
	row = None
	for a in ["text", "source", "location", "thumbnail_pic", "bmiddle_pic", "original_pic", "screen_name", "in_reply_to_screen_name"]:
	    if a in l and l[a] is not None:
		l[a] = l[a].encode("utf8")
	if "retweeted_status" in l and l["retweeted_status"] is not None:
	    l["retweeted_status"] = l["retweeted_status"]["id"]
	else:
	    if justretweets:
		continue
	if "user" in l:
	    if l["user"]["screen_name"] is not None:
		l["screen_name"] = l["user"]["screen_name"].encode("utf8")
	    elif l["user"]["name"] is not None:
		l["screen_name"] = l["user"]["name"].encode("utf8")
	    elif l["user"]["domain"] is not None:
		l["screen_name"] = l["user"]["domain"].encode("utf8")
	    else:
		l["screen_name"] = None
	else:
	    l["screen_name"] = None
	if "user" in l and l["user"] is not None:
	    l["user_id"] = l["user"]["id"]
	try:
	    row = pgconn.insert(table_name, l)
	except pg.ProgrammingError, pg.InternalError:
	    tobeginning_grace_count = 0
	    if not tobeginning and opt == 7:
		tobeginning_grace_count += 1 # have a bit of loose in case the next comments page contains some of the previous in sinacomments.sh iteration
		print "tobeginning_grace_count: " + str(tobeginning_grace_count)
		if tobeginning_grace_count > tobeginning_grace:
		    print last_one
		    print "UP-TO-DATE: comments up to date (duplicate found in DB)"
		    break
		else:
		    if not doupdate:
			continue
	    if not tobeginning and not doupdate:
		breakafterupdate = True
	    try:
		if doupdate:
		    row = pgconn.update(table_name, l)
		    print "updating..."
		    print row
		else:
		    pass
	    except:
		print "can't insert or update"
		print last_tweet
		pass
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
	if (insert_user or doupdate_user) and "user" in l and (opt == 7 or (opt == 1 and j == 0)):
	    u = l["user"]
	    u["retrieved"] = "NOW()"
	    for a in ["name", "screen_name", "location", "description", "profile_image_url", "url"]:
		if a in u and u[a] is not None:
		    u[a] = u[a].encode("utf8")
	    try:
		pgconn.insert("sinaweibo_users", u)
	    except pg.ProgrammingError, pg.InternalError:
		try:
		    if doupdate_user:
			if verbose:
			    print "user: trying to update instead"
			pgconn.update("sinaweibo_users", u)
		except:
		    print "user: an error has occurred (row cannot be updated)"
		if verbose:
		    print u
	if (j == len(js) - 1 or breakafterupdate) and "user" in l:
	    u = l["user"]
	    sql = "UPDATE sinaweibo_users SET posts_updated = NOW() WHERE id = %(id)d " % { "id": u["id"] }
	    pgconn.query(sql)
	if breakafterupdate:
	    if verbose:
		print "up to date. breaking..."
	    break
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
	try:
	    pgconn.insert(table_name, l)
	    if verbose:
		print "SUCCESS," + str(l["statuses_count"])
	except pg.ProgrammingError, pg.InternalError:
	    print "user duplicate found in DB..."
	    try:
		if doupdate:
		    print "trying to update instead"
		    pgconn.update(table_name, l)
		else:
		    print l
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
    tobeginning_grace_count = 0
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
		tobeginning_grace_count += 1 # have a bit of loose in case the next comments page contains some of the previous in sinacomments.sh iteration
		print "tobeginning_grace_count: " + str(tobeginning_grace_count)
		if tobeginning_grace_count > tobeginning_grace:
		    print last_one
		    print "UP-TO-DATE: comments up to date (duplicate found in DB)"
		    break
		else:
		    if not doupdate:
			continue
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
		    else:
			print u
		except:
		    print "user: an error has occurred (row cannot be updated)"
		    print u

f.close()
