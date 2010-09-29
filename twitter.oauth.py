#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import httplib
import simplejson
import time

import oauth2 as oauth
from oauthtwitter import OAuthApi
import pprint

import datetime
import csv

MAXIMUM_TRIES = 50

usage = "usage: twitter.oauth.py [1=mentions; 2=followers info by user_id, 3=single user info by screen_name,\
4=all tweets by user_id, 5=all tweets by screen_name]"
pgconn = pg.DB('jmsc', '127.0.0.1', 5432, None, None, 'jmsc', 'YOUR_PASSWORD')

sql_users_fields = "user_id,name,screen_name,description,profile_image_url,url,protected,followers_count,friends_count,created_at,\
favourites_count,utc_offset,time_zone,profile_background_image_url,profile_use_background_image,notifications,geo_enabled,verified,\
statuses_count,lang,contributors_enabled,follow_request_sent,listed_count,show_all_inline_media"

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
    except ValueError:
	print usage
	sys.exit()
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
	url = "http://api.twitter.com/1/statuses/user_timeline.json?user_id=" + str(user_id) + "&count=200&trim_user=1&include_rts=1&include_entities=1"
    elif opt == 5:
	url = "http://api.twitter.com/1/statuses/user_timeline.json?screen_name=" + screen_name + "&count=200&trim_user=1&include_rts=1&include_entities=1"
    else:
	sys.exit()
except pg.DatabaseError:
    pass

consumer_key = "IJIFqySugi5M42VyTrmTDQ"
consumer_secret = "5BrsbpTGV8TzQXXPkZ5aTBUBFjd9M7LjgrWgW1I"

oauth_token = "16495920-YJJ4TBRukyCGtCYmEerxhjQzfRfSgw3pg9CDsyOWW"
oauth_token_secret = "QlXZlp9ZqhTDjiYerVzMRZLuGXZUzl1FzyNNCbveaQ"

cmp_consumer_key = "ewRiBMvoxDj5BGKJkZ8b2Q"
cmp_consumer_secret = "gMLeBSCH3ci9UWbD6AhRZqCoOvYy2Ho3fmR2xLLMsE"

cmp_oauth_token = "131096208-5VLlH6VoHtDvyUviAxEMutEDdmT8fiXyKUVCK3Bs"
cmp_oauth_token_secret = "6MuAMhB2tK6zCSDTUnmNOdzNH3hQuklVNkSAbyiI"

request_token_url = 'http://twitter.com/oauth/request_token'
access_token_url = 'http://twitter.com/oauth/access_token'
authorize_url = 'http://twitter.com/oauth/authorize'

params = {
    'oauth_version': "1.0",
    'oauth_nonce': oauth.generate_nonce(),
    'oauth_timestamp': int(time.time())
}
consumer = oauth.Consumer(key = cmp_consumer_key, secret = cmp_consumer_secret)
token = oauth.Token(key = cmp_oauth_token, secret = cmp_oauth_token_secret)

if opt == 3:
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

#twitter = OAuthApi(consumer_key, consumer_secret, oauth_token, oauth_token_secret)

# Get the temporary credentials for our next few calls
#temp_credentials = twitter.getRequestToken()

# User pastes this into their browser to bring back a pin number
#print(twitter.getAuthorizationURL(temp_credentials))

# Get the pin # from the user and get our permanent credentials
#oauth_verifier = raw_input('What is the PIN? ')
#access_token = twitter.getAccessToken(temp_credentials, oauth_verifier)

#print("oauth_token: " + access_token['oauth_token'])
#print("oauth_token_secret: " + access_token['oauth_token_secret'])

# Do a test API call using our new credentials
#twitter = OAuthApi(consumer_key, consumer_secret, access_token['oauth_token'], access_token['oauth_token_secret'])
#user_timeline = twitter.GetUserTimeline()

pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(content)
#print content

if opt <= 3:
    resp, content = client.request(url, "GET")
    js = simplejson.loads(content)
if opt < 3:
    for x in js:
	if opt == 1:
	    print x['created_at'] + "\t" + x['text'] + "\t" + x['user']['screen_name'] + "\t" + x['user']['location'] + "\t" + x['user']['profile_image_url']
	elif opt == 2:
	    #print x
	    pp.pprint(x)
elif opt == 3:
    sql = "INSERT INTO twitter_users (retrieved," + sql_users_fields + ") VALUES (NOW(),"
    users_fields = sql_users_fields.split(",")
    d = dict()
    for f in users_fields:
	if f == "user_id":
	    d[f] = js["id"]
	else:
	    try:
		d[f] = js[f].encode("utf8")
	    except:
		d[f] = js[f]
	'''
	if f == "user_id":
	    f = "id"
	if js[f] is None:
	    sql += "null"
	elif f == "created_at":
    	    sql += datetime.datetime.strptime(js[f], "%a %b %d %H:%M:%S +0000 %Y").strftime('\'%Y-%m-%d %H:%M:%S\'')
	elif js[f] is True or js[f] is False:
	    sql += str(js[f]).upper()
	else:
	    try:
		intvalue = int(js[f])
		sql += str(intvalue)
	    except ValueError:
		#sql += "'" + js[f].encode("utf8").replace("'","''") + "'"
	    	sql += "'" + js[f].encode("utf8").replace("'","''") + "'"
	if f != "show_all_inline_media":
	    sql += ","
	'''
    sql += ")"
    d['retrieved'] = "NOW()"
    #print sql
    #sel = pgconn.query(sql)
    inserted = pgconn.insert("twitter_users", d)
elif opt == 4 or opt == 5:
    dt = datetime.datetime.now()
    dtstr = datetime.datetime.strftime(dt,'%Y%m%d%H%M')
    print dtstr
    if opt == 4:
	fname = str(user_id) + "_" + dtstr + ".csv"
	print "user_id: " + str(user_id)
    else:
	fname = screen_name + "_" + dtstr + ".csv"
	print "@" + screen_name
    f = open(fname, "w")
    cw = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar="\\", lineterminator="\n")
    #missed_once = False
    cw.writerow(["id", "created_at", "text", "in_reply_to_user_id", "in_reply_to_screen_name", "in_reply_to_status_id"])
    for i in range(20):
	#f = open(dtstr + "_" + "%02d" % str(i) + ".tsv", "rw")
	page = i + 1
	resp, content = client.request(url + "&page=" + str(page), "GET")
	print resp
	tries = 0
	while resp['status'] != '200' and tries < MAXIMUM_TRIES:
	    tries += 1
	    print "trying " + str(tries)
	    resp, content = client.request(url + "&page=" + str(page), "GET")
	    print resp
	    time.sleep(5)
	    if resp['status'] == '400':
		if int(resp['x-ratelimit-remaining']) <= 0:
		    time.sleep(300)
	if resp['status'] == '200':
	    js = simplejson.loads(content)
	    if int(resp['x-ratelimit-remaining']) <= 30:
		time.sleep(2400)
	elif tries >= MAXIMUM_TRIES:
	    f.write("ERROR: maximum tries")
	    sys.exit()
	else:
	    f.write("ERROR: status " + str(resp['status']))
	    sys.exit()
    	'''
	    if missed_once:
		break
	    missed_once = True
	    continue
	'''
	for j in range(len(js)):
	    l = js[j]
	    r = list()
	    r = [l["id"], l["created_at"], l["text"].encode("utf8"), l["in_reply_to_user_id"], l["in_reply_to_screen_name"], l["in_reply_to_status_id"]]
	    cw.writerow(r)
	print(len(js))
	if len(js) <= 0:
	    break
	time.sleep(1)
    f.close()
