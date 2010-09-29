# -*- coding: utf-8 -*-

import sys
import pg
import httplib
import simplejson
import datetime
import oauth2 as oauth
import pprint

pgconn = pg.connect('jmsc', '127.0.0.1', 5432, None, None, 'jmsc', 'YOUR_PASSWORD')

no_duplicates = False
is_oauth = False
if len(sys.argv) > 1:
    user_id = sys.argv[1]
    if len(sys.argv) > 2:
	for i in range(2,len(sys.argv)):
	    if sys.argv[i] == "-nd" or sys.argv[i] == "--no-duplicates":
		no_duplicates = True
	    if sys.argv[i] == "-o" or sys.argv[i] == "--oauth":
		is_oauth = True
else:
    print "user_id missing"
    sys.exit()

try:
    user_id = str(int(user_id))
except (ValueError):
    print "argument invalid: given " + user_id
    sys.exit()

if no_duplicates:
    res = pgconn.query("SELECT COUNT(*) FROM twitter_users WHERE user_id = " + str(user_id)).getresult()
    #print res[0][0]
    if res[0][0] > 0:
	print "duplicate has been found: this script will exit..."
	sys.exit()

if user_id > 0:
    conn = httplib.HTTPConnection("api.twitter.com")
    ok = False
    if is_oauth:
	cmp_consumer_key = "ewRiBMvoxDj5BGKJkZ8b2Q"
	cmp_consumer_secret = "gMLeBSCH3ci9UWbD6AhRZqCoOvYy2Ho3fmR2xLLMsE"
	cmp_oauth_token = "131096208-5VLlH6VoHtDvyUviAxEMutEDdmT8fiXyKUVCK3Bs"
	cmp_oauth_token_secret = "6MuAMhB2tK6zCSDTUnmNOdzNH3hQuklVNkSAbyiI"
	consumer = oauth.Consumer(key = cmp_consumer_key, secret = cmp_consumer_secret)
	token = oauth.Token(key = cmp_oauth_token, secret = cmp_oauth_token_secret)
	client = oauth.Client(consumer, token)
	resp, content = client.request("http://api.twitter.com/1/users/show.json?user_id=" + user_id, "GET")
	r = content
	if len(r) > 2:
	    ok = True
	    j = simplejson.loads(r)
    else:
	try:
	    conn.request("GET", "/1/users/show.json?user_id=" + user_id)
	except (Exception):
	    sys.exit(sys.exc_info())
	r = conn.getresponse()
	if r.status == 200:
	    ok = True
	    j = simplejson.load(r)
    if ok:
	v = { "user_id": None, "name": None, "screen_name": None, "description": None, "profile_image_url": None, \
	"url": None, "protected": None, "followers_count": None, "friends_count": None, "created_at": None, "favourites_count": None, "utc_offset": None, "time_zone": None,\
	"profile_background_image_url": None, "profile_use_background_image": None, "notifications": None, "geo_enabled": None, "verified": None, "following": None,\
	"statuses_count": None, "lang": None, "contributors_enabled": None, "follow_request_sent": None, "listed_count": None, "show_all_inline_media": None }
	sql = "INSERT INTO twitter_users (retrieved,"\
	+"user_id, name, screen_name, description, profile_image_url,"\
	+"url, protected, followers_count, friends_count, created_at, favourites_count, utc_offset, time_zone,"\
	+"profile_background_image_url, profile_use_background_image, notifications, geo_enabled, verified, following,"\
	+"statuses_count, lang, contributors_enabled, follow_request_sent, listed_count, show_all_inline_media"\
	+") VALUES ("\
	+"NOW(), %(user_id)d, '%(name)s', '%(screen_name)s', '%(description)s', '%(profile_image_url)s',"\
	+"'%(url)s', %(protected)s, %(followers_count)d, %(friends_count)d, '%(created_at)s', %(favourites_count)d, %(utc_offset)d, '%(time_zone)s',"\
	+"'%(profile_background_image_url)s', %(profile_use_background_image)s, %(notifications)s, %(geo_enabled)s, %(verified)s, %(following)s,"\
	+"%(statuses_count)d, '%(lang)s', %(contributors_enabled)s, %(follow_request_sent)s, %(listed_count)d, %(show_all_inline_media)s) "

	print j
	for key in v:
	    if not key in j:
		v[key] = "null"
	    #if key == "protected" or key == "profile_use_background_image" or key == "notifications" or key == "geo_enabled" \
	    #or key == "verified" or key == "contributors_enabled" or key == "follow_request_sent" or key == "show_all_inline_media":
	    if key == "user_id":
		v[key] = j["id"]
	    elif key not in j or j[key] is None:
		v[key] = "null"
		if key == "name" or key == "description" or key == "profile_image_url" or key == "profile_background_image_url" or key == "url" or key == "time_zone":
		    v[key] = None
		if key == "utc_offset" or key == "followers_count" or key == "friends_count" or key == "favourites_count" or key == "utc_offset" or key == "statuses_count" or key == "listed_count":
		    v[key] = 0
	    elif key == "following":
		v[key] = "null"
	    elif key == "created_at":
		v[key] = datetime.datetime.strptime(j[key], "%a %b %d %H:%M:%S +0000 %Y").strftime('%Y-%m-%d %H:%M:%S')
	    elif key == "name" or key == "description" or key == "profile_image_url" or key == "profile_background_image_url" or key == "url" or key == "time_zone":
		v[key] = j[key].encode("utf8").replace("'","''")
	    elif j[key] is 0:
		v[key] = 0
	    elif j[key] is True:
		v[key] = "true"
	    elif j[key] is False:
		v[key] = "false"
	    else:
		v[key] = j[key]
	sql = str(sql % v)
	sel = pgconn.query(sql)
	print str(j["id"]) + "\t" + j["screen_name"]
	#sel = pgconn.query("INSERT INTO twitter_users (retrieved, user_id, screen_name) VALUES (NOW(), 1, 'cedric')")
	#sel = pgconn.query("SELECT * FROM twitter_users ")
    else:
	print r
