#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import mypass
import httplib
import simplejson
import time
import socket

import oauth2 as oauth
import pprint

import datetime
import csv
import types

MAXIMUM_TRIES = 50

usage = "usage: twitter.oauth.py [1=mentions; 2=followers info by user_id, 3=single user info by screen_name,\
4=all tweets by user_id, 5=all tweets by screen_name] ID [-d|--database||-c|--csv-out||-b|--to-beginning]"

psql_dateformat = '%Y-%m-%d %H:%M:%S %Z'
twitter_dateformat = '%a %b %d %H:%M:%S +0000 %Y'

def getRangePartitionByDate(created_at_str):
    try:
	created_at = datetime.datetime.strptime(created_at_str, twitter_dateformat)
    except ValueError:
	try:
	    created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
	except ValueError:
	    try:
		created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M")
	    except ValueError:
		try:
		    created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%d")
		except ValueError:
		    print created_at_str
		    sys.exit()
    isocal = created_at.isocalendar()
    return "twitter.rp_tweets_y" + str(isocal[0]) + "w" + str(isocal[1])


pgconn = mypass.getConn()

sql_users_fields = "user_id,name,screen_name,description,profile_image_url,url,protected,followers_count,friends_count,created_at,\
favourites_count,utc_offset,time_zone,profile_background_image_url,profile_use_background_image,notifications,geo_enabled,verified,\
statuses_count,lang,contributors_enabled,follow_request_sent,listed_count,show_all_inline_media"

todb = False
tocsv = True
tobeginning = False
doupdate = False
verbose = False

socket.setdefaulttimeout(30)

time_db = 0
time_api = 0
start_time_api = time.time()

if len(sys.argv) <= 1:
    print usage
    sys.exit()

if len(sys.argv) > 1:
    try:
	opt = int(sys.argv[1])
    except ValueError:
	print usage
	sys.exit()

if len(sys.argv) > 2:
    try:
    	if opt == 2 or opt == 4:
	    user_id = int(sys.argv[2])
    	elif opt == 3 or opt == 5:
	    screen_name = str(sys.argv[2])
	elif opt == 6:
	    tid = long(sys.argv[2])
    except ValueError:
	print usage
	sys.exit()
    for i in range(3,len(sys.argv)):
	if sys.argv[i] == "-co" or sys.argv[i] == "--csv-out":
	    tocsv = True
	    todb = False
	if sys.argv[i] == "-d" or sys.argv[i] == "--database":
	    tocsv = False
	    todb = True
	if sys.argv[i] == "-b" or sys.argv[i] == "--to-beginning":
	    tobeginning = True
	if sys.argv[i] == "-u" or sys.argv[i] == "--update":
	    doupdate = True
	if sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
	    verbose = True
try:
    if opt == 1:
	url = "http://api.twitter.com/1/statuses/mentions.json?count=800&include_rts=true&include_entities=true"
    elif opt == 2:
	url = "http://api.twitter.com/1/statuses/followers.json?user_id=" + user_id + "&include_entities=true&count=100"
    elif opt == 3:
	url = "http://api.twitter.com/1/users/show.json?screen_name=" + screen_name + "&include_entities=true&count=100"
	#res = pgconn.query("SELECT COUNT(*) FROM twitter_users WHERE screen_name = '%s' " % screen_name.replace("'","''"))
    	res = pgconn.get("twitter_users", { "screen_name": screen_name }, "screen_name")
	if len(res) > 0:
	    print "duplicate has been found: this script will exit..."
	    sys.exit()
    elif opt == 4:
	url = "http://api.twitter.com/1/statuses/user_timeline.json?user_id=" + str(user_id) + "&count=200&trim_user=0&include_rts=1&include_entities=1"
    elif opt == 5:
	url = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=" + screen_name + "&count=200&trim_user=1&include_rts=1&include_entities=1"
    elif opt == 6:
	url = "http://api.twitter.com/1/statuses/show/%d.json" % tid
    else:
	sys.exit()
except pg.DatabaseError:
    pass

twitterOauth = mypass.getTwitterOauth()

consumer_key = twitterOauth["consumer_key"]
consumer_secret = twitterOauth["consumer_secret"]
oauth_token = twitterOauth["oauth_token"]
oauth_token_secret = twitterOauth["oauth_token_secret"]

request_token_url = 'http://twitter.com/oauth/request_token'
access_token_url = 'http://twitter.com/oauth/access_token'
authorize_url = 'http://twitter.com/oauth/authorize'

params = {
    'oauth_version': "1.0",
    'oauth_nonce': oauth.generate_nonce(),
    'oauth_timestamp': int(time.time())
}
consumer = oauth.Consumer(key = consumer_key, secret = consumer_secret)
token = oauth.Token(key = oauth_token, secret = oauth_token_secret)

# Set our token/key parameters
params['oauth_token'] = token.key
params['oauth_consumer_key'] = consumer.key

req = oauth.Request(method="GET", url=url, parameters=params)

# Sign the request.
signature_method = oauth.SignatureMethod_HMAC_SHA1()
req.sign_request(signature_method, consumer, token)

client = oauth.Client(consumer, token)

pp = pprint.PrettyPrinter(indent=4)

if opt <= 3 or opt == 6:
    resp, content = client.request(url, "GET")
    js = simplejson.loads(content)

time_api = time.time() - start_time_api

start_time_db = time.time()

if opt < 3:
    for x in js:
	if opt == 1:
	    print x['created_at'] + "\t" + x['text'] + "\t" + x['user']['screen_name'] + "\t" + x['user']['location'] + "\t" + x['user']['profile_image_url']
	elif opt == 2:
	    #print x
	    pp.pprint(x)
elif opt == 6:
    l = js
    r = {"id": l["id"], "created_at": l["created_at"], "text": l["text"].encode("utf8"), "in_reply_to_user_id": l["in_reply_to_user_id"],\
	"in_reply_to_status_id": l["in_reply_to_status_id"], "retweet_count": l["retweet_count"]}
    if "retweeted_status" in l:
	if l["retweeted_status"] is not None:
	    r["retweeted_status"] = l["retweeted_status"]["id"]
    r["user_id"] = l["user"]["id"]
    r["screen_name"] = l["user"]["screen_name"]
    try:
	if verbose:
	    print "Inserting..."
	tablename = getRangePartitionByDate(r["created_at"])
	row = pgconn.insert(tablename, r)
    except pg.ProgrammingError, pg.InternalError:
	#print pgconn.error
	if pgconn.error.find('duplicate key value violates unique constraint') < 0:
	    print pgconn.error
	try:
	    if doupdate:
		print "Updating..."
    		pgconn.update(tablename, r)
	except:
	    #print r
	    print pgconn.error
	    print "an error has occurred (row cannot be updated)"

# Add user
if opt == 3 or opt == 6:
    #sql = "INSERT INTO twitter_users (retrieved," + sql_users_fields + ") VALUES (NOW(),"
    users_fields = sql_users_fields.split(",")
    ulist = list()
    if opt == 3:
	ulist.append({"user": js})
    elif opt == 6:
	ulist.append(js)
    #print js
    for l in ulist:
	if verbose:
	    print l
	d = dict()
	for f in users_fields:
	    if f == "user_id":
		d[f] = js["user"]["id"]
		d["id"] = js["user"]["id"]
	    else:
		try:
		    d[f] = js["user"][f].encode("utf8")
		except:
		    d[f] = js["user"][f]
	#sql += ")"
	d['retrieved'] = "NOW()"
	#print sql
	#sel = pgconn.query(sql)
	try:
	    if verbose:
		print d
		print "Try insert"
	    inserted = pgconn.insert("twitter_users", d)
	except pg.ProgrammingError, pg.InternalError:
	    if verbose:
		print "Try update"
	    if doupdate:
		updated = pgconn.update("twitter_users", d)

if opt == 4 or opt == 5:
    dt = datetime.datetime.now()
    dtstr = datetime.datetime.strftime(dt,'%Y%m%d%H%M')
    tolerance_max = 10
    tolerance_count = 0
    if verbose:
	print dtstr
    if opt == 4:
	fname = str(user_id) + "_" + dtstr + ".csv"
	if verbose:
	    print "user_id: " + str(user_id)
    else:
	fname = screen_name + "_" + dtstr + ".csv"
	if verbose:
	    print "@" + screen_name
    if tocsv:
	f = open(fname, "w")
	cw = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar="\\", lineterminator="\n")
	cw.writerow(["id", "created_at", "text", "in_reply_to_user_id", "in_reply_to_screen_name", "in_reply_to_status_id", "screen_name", "user_id"])
    elif todb:
    	if verbose:
    	    print "to DB"
    #missed_once = False
    succeeded = 0
    failed = 0
    for i in range(20):
	#f = open(dtstr + "_" + "%02d" % str(i) + ".tsv", "rw")
	if tolerance_count > tolerance_max:
	    break
	page = i + 1
	tolerance_count = 0
	if verbose:
	    print url
	resp, content = client.request(url + "&page=" + str(page), "GET")
	if verbose:
	    print resp
	    print content
	tries = 0
	while resp['status'] != '200' and tries < MAXIMUM_TRIES:
	    tries += 1
	    print "trying " + str(tries)
	    resp, content = client.request(url + "&page=" + str(page), "GET")
	    if verbose:
		print resp['status']
	    print resp
	    time.sleep(0.1)
	    if resp['status'] == '400':
		if int(resp['x-ratelimit-remaining']) <= 0:
		    time.sleep(100)
	    elif resp['status'] == '401':
		print "unauthorized 401: " + str(user_id)
		break
	if resp['status'] == '200':
	    js = simplejson.loads(content)
	    if int(resp['x-ratelimit-remaining']) <= 20:
		time.sleep(400)
	elif tries >= MAXIMUM_TRIES:
	    if tocsv:
		f.write("ERROR: maximum tries")
	    else:
		print "ERROR: maximum tries"
	    sys.exit()
	else:
	    if tocsv:
		f.write("ERROR: status " + str(resp['status']))
	    else:
		print "ERROR: status " + str(resp['status'])
	    sys.exit()
	last_tweet = None
	for j in range(len(js)):
	    l = js[j]
	    last_tweet = l
	    if l["in_reply_to_user_id"] != None and type(l["in_reply_to_user_id"]) is types.StringType and len(l["in_reply_to_user_id"]) == 2:
		l["in_reply_to_user_id"] = None
	    if tocsv:
		r = list()
		r = [l["id"], l["created_at"], l["text"].encode("utf8"), l["in_reply_to_user_id"], l["in_reply_to_screen_name"], l["in_reply_to_status_id"]]
		if opt == 4:
		    r.extend(["",user_id])
		elif opt == 5:
		    r.append(screen_name)
		    if l["user"] is not None:
			r.append(l["user"]["id"])
		    else:
			r.append("")
		cw.writerow(r)
	    elif todb:
		try:
		    r = dict()
		    row = None
		    r = {"id": l["id"], "created_at": l["created_at"], "text": l["text"].encode("utf8"), "in_reply_to_user_id": l["in_reply_to_user_id"],\
			"in_reply_to_status_id": l["in_reply_to_status_id"]}
		    #print l
		    if "retweet_count" in l:
			r["retweet_count"] = l["retweet_count"]
		    if "retweeted_status" in l:
			if l["retweeted_status"] is not None:
			    r["retweeted_status"] = l["retweeted_status"]["id"]
		    if opt == 4:
			r["user_id"] = user_id
			if "screen_name" in l["user"]:
			    r["screen_name"] = l["user"]["screen_name"]
		    elif opt == 5:
			if l["user"] is not None:
			    r["user_id"] = l["user"]["id"]
			r["screen_name"] = screen_name
		    #print r
		    if "geo" in l and l["geo"] is not None:
			if "type" in l["geo"] and l["geo"]["type"] == "Point" and "coordinates" in l["geo"] and l["geo"]["coordinates"] is not None and len(l["geo"]["coordinates"]) == 2:
			    lat = l["geo"]["coordinates"][0]
			    lng = l["geo"]["coordinates"][1]
			    wkt_point = "POINT(" + str(lng) + " " + str(lat) + ")"
			    r["geo"] = "SRID=4326;" + wkt_point
			    '''
			    sql = "UPDATE %(table_name)s SET geo = ST_GeomFromText('%(wkt_point)s', 4326) WHERE id = %(id)d " % {"table_name": "rp_tweets", "wkt_point": wkt_point, "id": row["id"]}
			    try:
				pgconn.query(sql)
			    except:
				print sql
				print "geo error: " + wkt_point
			    '''
		    if verbose:
			print r
		    tablename = getRangePartitionByDate(r["created_at"])
		    row = pgconn.insert(tablename, r)
		    succeeded += 1
		except pg.ProgrammingError, pg.InternalError:
		    if not tobeginning:
			tolerance_count += 1
			if verbose:
			    print last_tweet
			    print "tweets up to date (duplicate found in DB)"
			if tolerance_count > tolerance_max:
			    break
			else:
			    continue
		    try:
			if doupdate:
			    pgconn.update(tablename, r)
			    if verbose:
				print "update successful"
			else:
			    if verbose:
				print last_tweet
				print "tweets up to date (duplicate found in DB) -b"
		    except:
			if verbose:
			    print "an error has occurred (row cannot be updated)"
	if verbose:
	    print(len(js))
	if len(js) <= 0:
	    break
	try:
	    sql = "UPDATE twitter_users SET posts_updated = NOW() WHERE id = %d " % user_id
	    pgconn.query(sql)
	except pg.ProgrammingError, pg.InternalError:
	    pass
	time.sleep(0.1)
    if tocsv:
	f.close()

time_db = time.time() - start_time_db

if verbose:
    print "API time: " + str(time_api)
    print "DB time: " + str(time_db)
    print "Succeeded: " + str(succeeded)
    print "Failed: " + str(failed)
