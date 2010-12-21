#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import httplib
import simplejson
import datetime
import oauth2 as oauth
import pprint
import mypass

pgconn = mypass.getConn()

table_name = "twitter_users"

user_id = 0
screen_name = ""

no_overwrite = False
is_oauth = True
force_screenname = False
if len(sys.argv) > 1:
    if len(sys.argv) > 2:
	for i in range(2,len(sys.argv)):
	    if sys.argv[i] == "-no" or sys.argv[i] == "--no-overwrite":
		no_overwrite = True
	    if sys.argv[i] == "-u" or sys.argv[i] == "--update":
		no_overwrite = False
	    if sys.argv[i] == "-o" or sys.argv[i] == "--oauth":
		is_oauth = True
	    if sys.argv[i] == "-na" or sys.argv[i] == "--no-auth":
		is_oauth = False
	    if sys.argv[i] == "-fs" or sys.argv[i] == "--force-screenname":
		force_screenname = True
    try:
	if force_screenname:
	    screen_name = str(sys.argv[1])
	else:
	    user_id = long(sys.argv[1])
    except ValueError:
	screen_name = str(sys.argv[1])
else:
    print "user_id or screen_name missing"
    sys.exit()

if user_id > 0 or len(screen_name) > 0:
    conn = httplib.HTTPConnection("api.twitter.com")
    ok = False
    if is_oauth:
	twitterOauth = mypass.getTwitterOauth()

	consumer_key = twitterOauth["consumer_key"]
	consumer_secret = twitterOauth["consumer_secret"]
	oauth_token = twitterOauth["oauth_token"]
	oauth_token_secret = twitterOauth["oauth_token_secret"]

	consumer = oauth.Consumer(key = consumer_key, secret = consumer_secret)
	token = oauth.Token(key = oauth_token, secret = oauth_token_secret)
	client = oauth.Client(consumer, token)
	if user_id > 0 and not force_screenname:
	    resp, content = client.request("http://api.twitter.com/1/users/show.json?user_id=" + str(user_id), "GET")
	else:
	    resp, content = client.request("http://api.twitter.com/1/users/show.json?screen_name=" + screen_name, "GET")
	r = content
	if len(r) > 2:
	    ok = True
	    j = simplejson.loads(r)
	else:
	    print r
	if "error" in j:
	    print "Error: " + j["error"]
	    ok = False
    else:
	try:
	    if user_id > 0 and not force_screenname:
		conn.request("GET", "/1/users/show.json?user_id=" + user_id)
	    else:
		conn.request("GET", "/1/users/show.json?screen_name=" + screen_name)
	except (Exception):
	    sys.exit(sys.exc_info())
	r = conn.getresponse()
	if r.status == 200:
	    ok = True
	    j = simplejson.load(r)
    if ok:
	l = j
	# adjustments for non-required fields that might be unicode
	if l["description"] is not None:
	    l["description"] = l["description"].encode("utf8")
	if l["location"] is not None:
	    l["location"] = l["location"].encode("utf8")
	if l["url"] is not None:
	    l["url"] = l["url"].encode("utf8")
	if l["profile_image_url"] is not None:
	    l["profile_image_url"] = l["profile_image_url"].encode("utf8")
	if l["profile_background_image_url"] is not None:
	    l["profile_background_image_url"] = l["profile_background_image_url"].encode("utf8")
    	r = {"id": l["id"], "name": l["name"].encode("utf8"), "screen_name": l["screen_name"],
	"description": l["description"], "profile_image_url": l["profile_image_url"],
	"url": l["url"], "followers_count": l["followers_count"],
	"utc_offset": l["utc_offset"], "time_zone": l["time_zone"], "profile_background_image_url": l["profile_background_image_url"],
	"friends_count": l["friends_count"],"created_at": l["created_at"], "favourites_count": l["favourites_count"],
	"notifications": l["notifications"],"geo_enabled": l["geo_enabled"],
	"protected": l["protected"],
	"verified": l["verified"], "statuses_count": l["statuses_count"], "lang": l["lang"],
	"contributors_enabled": l["contributors_enabled"], "follow_request_sent": l["follow_request_sent"],
	"listed_count": l["listed_count"], "show_all_inline_media": l["show_all_inline_media"],
	"location": l["location"],
	"retrieved": "NOW()"}
	try:
	    pgconn.insert(table_name, r)
	except pg.ProgrammingError, pg.InternalError:
	    try:
		if not no_overwrite:
		    print "user duplicate found in DB... trying to update instead"
		    pgconn.update(table_name, r)
	    except:
		print "an error has occurred (row cannot be updated)"
	    print r
