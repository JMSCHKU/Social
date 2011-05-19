#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import mypass
import httplib
import simplejson
import time

import oauth2 as oauth
import pprint

import datetime
import csv
import types

import weibopy # we use our own slightly-extended version of weibopy
import unittest
#from weibopy.auth import OAuthHandler, BasicAuthHandler
#from weibopy.api import API

class SinaWeiboOauth():
    sinaweiboOauth = mypass.getSinaWeiboOauth()
    pgconn = None
    toleranceNotToBeginning = 5 # in fetching timelines, break from loop when toleranceNotToBeginning consecutive statuses already exist in the DB

    def getAtt(self, obj, key):
        try:
            return obj.__getattribute__(key)
        except Exception, e:
            return None

    def setAtt(self, obj, key, value):
        try:
            return obj.__setattribute__(key, value)
        except Exception, e:
            return None

    def setToken(self, token, tokenSecret):
        self.auth = weibopy.auth.OAuthHandler(self.sinaweiboOauth["consumer_key"], self.sinaweiboOauth["consumer_secret"])
        self.auth.setToken(token, tokenSecret)
        self.api = weibopy.API(self.auth)

    def auth(self):
        self.auth = weibopy.auth.OAuthHandler(self.sinaweiboOauth["consumer_key"], self.sinaweiboOauth["consumer_secret"])
        auth_url = self.auth.get_authorization_url()
        print 'Please authorize: ' + auth_url
        verifier = raw_input('PIN: ').strip()
        self.auth.get_access_token(verifier)
        self.api = weibopy.API(self.auth)

    def status_to_row(self, status):
	x = dict()
	x["created_at"] = self.getAtt(status, "created_at").strftime("%Y-%m-%d %H:%M:%S")
	for a in ["text", "source", "location", "thumbnail_pic", "bmiddle_pic", "original_pic", "screen_name", "in_reply_to_screen_name"]:
	    try:
		att = self.getAtt(status, a)
		x[a] = att.encode("utf8")
	    except:
		x[a] = att
	for a in ["id", "in_reply_to_user_id", "in_reply_to_status_id", "truncated"]:
	    x[a] = self.getAtt(status, a)
	try:
	    rts = self.getAtt(self.getAtt(status, "retweeted_status"), "id")
	except:
	    rts = None
	if rts is not None:
	    x["retweeted_status"] = rts
	try:
	    user_id = self.getAtt(self.getAtt(status, "user"), "id")
	except:
	    user_id = None
	try:
	    screen_name = self.getAtt(self.getAtt(status, "user"), "screen_name").encode("utf8")
	except:
	    screen_name = None
	if user_id is not None:
	    x["user_id"] = user_id
	if screen_name is not None:
	    x["screen_name"] = screen_name
	try:
	    geo = self.getAtt(status, "geo")
	    coord = self.getAtt(geo, "coordinates")
	except:
	    geo = None
	if geo is not None and coord is not None and len(coord) > 0:
	    #print coord
	    lat = coord[0]
	    lng = coord[1]
	    wkt_point = "POINT(" + str(lat) + " " + str(lng) + ")"
	    print coord + " " + wkt_point
	    sql = "UPDATE %(table_name)s SET geo = ST_GeomFromText('%(wkt_point)s', 4326) WHERE id = %(id)d " % {"table_name": "sinaweibo", "wkt_point": wkt_point, "id": x["id"]}
	    try:
		pgconn.query(sql)
	    except:
		print sql
		print "geo error: " + wkt_point
	return x

    def user_to_row(self, user):
	x = dict()
	x["created_at"] = self.getAtt(user, "created_at").strftime("%Y-%m-%d %H:%M:%S")
	x["retrieved"] = "NOW()"
	for a in ["name", "screen_name", "location", "description", "profile_image_url", "url"]:
	    try:
		att = self.getAtt(user, a)
		x[a] = att.encode("utf8")
	    except:
		x[a] = att
	for a in ["id", "province", "city", "domain", "gender", "followers_count", "friends_count", "favourites_count", \
"time_zone", "profile_background_image_url", "profile_use_background_image", "allow_all_act_msg", "geo_enabled", "verified", "following", "statuses_count"]:
	    x[a] = self.getAtt(user, a)
	return x

    def comment_to_row(self, comment):
	x = dict()
	x["created_at"] = self.getAtt(comment, "created_at").strftime("%Y-%m-%d %H:%M:%S")
	try:
    	    text = self.getAtt(comment, "text")
	    if len(text) > 0:
		x["text"] = text.encode("utf8")
	except:
    	    x["text"] = text
	x["id"] = self.getAtt(comment, "id")
	x["user_id"] = self.getAtt(self.getAtt(comment, "user"), "id")
	return x

    def user_timeline(self, user_id, count=200, page=1, toDB=True, toBeginning=True):
	start_time_api = time.time()
        timeline = self.api.user_timeline(count=count, page=page, user_id=user_id)
	time_api = time.time() - start_time_api
	r = self.status_timeline(timeline)
	r["time_api"] = time_api
	return r

    def reposts(self, status_id, count=200, page=1, toDB=True, toBeginning=True):
	start_time_api = time.time()
        timeline = self.api.repost_timeline(count=count, page=page, id=status_id)
	time_api = time.time() - start_time_api
	r = self.status_timeline(timeline, False, toDB, toBeginning)
	r["time_api"] = time_api
	return r

    # common function to go through a timeline and optionally put in the DB
    def status_timeline(self, statuses, isSingleUser=True, toDB=True, toBeginning=False):
	already_exists_count = 0
	time_db = 0
	time_db_u = 0
	timeline_users_ids = list()
	toleranceNotToBeginningCount = 0
        for l in statuses:
	    x = self.status_to_row(l)
	    if toDB:
		start_time_db = time.time()
		resp = self.toDB("sinaweibo", x)
		time_db += time.time() - start_time_db
		if not resp["already_exists"] and resp["success"] and not isSingleUser:
		    timeline_user = self.getAtt(l, "user")
		    timeline_user_id = self.getAtt(timeline_user, "id")
		    #print resp
		    if not timeline_user_id in timeline_users_ids:
			start_time_db_u = time.time()
			u = self.user_to_row(timeline_user)
			resp_u = self.toDB("sinaweibo_users", u)
			time_db_u += time.time() - start_time_db_u
			if resp_u["already_exists"] or resp_u["success"]:
			    timeline_users_ids.append(timeline_user_id)
		if resp["already_exists"]:
		    if toBeginning:
			already_exists_count += 1
		    else:
			toleranceNotToBeginningCount += 1
			if toleranceNotToBeginningCount > self.toleranceNotToBeginning:
			    break
		else:
		    if not toBeginning:
			toleranceNotToBeginningCount = 0
	    else:
		print x
	if isSingleUser and toDB and len(statuses) > 0:
	    start_time_db_u = time.time()
	    u = self.user_to_row(self.getAtt(statuses[0], "user"))
	    u["posts_updated"] = "NOW()"
	    resp_u = self.toDB("sinaweibo_users", u, True)
	    #print resp_u
	    time_db_u += time.time() - start_time_db_u
	r = { "count": len(statuses) }
	if toDB:
	    if toBeginning:
		r["already_exists_count"] = already_exists_count 
	    r["time_db"] = time_db
	    r["time_db_u"] = time_db_u
	return r

    def comments(self, status_id, count=200, page=1, toDB=True, toBeginning=True):
	already_exists_count = 0
	start_time_api = time.time()
	comments = self.api.comments(id=status_id, count=count, page=page)
	time_api = time.time() - start_time_api
	time_db = 0
	time_db_u = 0
	comments_users_ids = list()
        for l in comments:
	    x = self.comment_to_row(l)
	    x["status_id"] = status_id
	    if toDB:
		start_time_db = time.time()
		resp = self.toDB("sinaweibo_comments", x)
		time_db += time.time() - start_time_db
		# user information
		comment_user = self.getAtt(l, "user")
		comment_user_id = self.getAtt(comment_user, "id")
		if not resp["already_exists"] and resp["success"] and not comment_user_id in comments_users_ids: # update a user once per cycle
		    start_time_db_u = time.time()
		    u = self.user_to_row(comment_user)
		    resp_u = self.toDB("sinaweibo_users", u)
		    time_db_u += time.time() - start_time_db_u
		    if resp_u["already_exists"] or resp_u["success"]:
			comments_users_ids.append(comment_user_id)
		#print resp
		if resp["already_exists"]:
		    if toBeginning:
			already_exists_count += 1
		    else:
			break
	    else:
		print x
	r = { "count": len(comments), "time_api": time_api, "page": page }
	if toDB:
	    if toBeginning:
		r["already_exists_count"] = already_exists_count 
	    r["time_db"] = time_db
	    r["time_db_u"] = time_db_u
	return r

    def user(self, user_id, screen_name=None, toDB=True):
	start_time_api = time.time()
	if screen_name is not None:
	    user = self.api.get_user(screen_name=screen_name)
	else:
	    user = self.api.get_user(user_id=user_id)
	time_api = time.time() - start_time_api
	time_db = 0
	x = self.user_to_row(user)
	if toDB:
	    start_time_db = time.time()
	    resp = self.toDB("sinaweibo_users", x, True)
	    time_db = time.time() - start_time_db
	    if resp["already_exists"]:
		already_exists = True
	    else:
		already_exists = False
	    resp["time_db"] = time_db
	    resp["already_exists"] = already_exists
	    resp["newdata"] = x
	    #print resp
	else:
	    print x
	if toDB:
	    r = resp
	else:
	    r = dict()
	r["time_api"] = time_api
	return r

    def socialgraph(self, user_id, rel="followers", cursor=-1, count=5000, toDB=True):
	already_exists_count = 0
	time_db = 0
	start_time_api = time.time()
	if rel == "friends":
	    relations = self.api.friends_ids(user_id=user_id, cursor=cursor, count=count)
	else:
	    relations = self.api.followers_ids(user_id=user_id, cursor=cursor, count=count)
	fids = self.getAtt(relations, "ids")
	time_api = time.time() - start_time_api
	for fid in fids:
	    x = { "source_id": user_id, "target_id": fid, "retrieved": "NOW()" } 
	    start_time_db = time.time()
	    resp = self.toDB("sinaweibo_" + rel, x, True)
	    time_db += time.time() - start_time_db
	    if resp["already_exists"]:
		already_exists_count += 1
	r = { r["ids"]: fids, r["time_api"]: time_api, r["count"]: len(fids) }
	if toDB:
	    r["time_db"] = time_db
	    r["already_exists_count"] = already_exists_count
	return r

    def toDB(self, tablename, data, doupdate=False):
	if self.pgconn is None:
	    self.pgconn = mypass.getConn()
	resp = { "success": False, "already_exists": False }
	try:
	    self.pgconn.insert(tablename, data)
	    success = True
	except pg.ProgrammingError, pg.InternalError:
	    if self.pgconn.error.find('duplicate key value violates unique constraint') > 0:
		resp["already_exists"] = True
    		try:
    		    if doupdate:
    			self.pgconn.update(tablename, data)
    			resp["success"] = True
    		except:
    		    pass
	#pgconn.close()
	return resp

sw = SinaWeiboOauth()
#sw.auth()
sw.setToken(sw.sinaweiboOauth["oauth_token"], sw.sinaweiboOauth["oauth_token_secret"]) 
#sw.setToken("24910039392f0acf7b83b8cb91ee9191", "1363bae989c232bf5db6aefb3e6460c7")
print sw.user_timeline(1801443400)
print sw.comments(10741815655)
print sw.reposts(10713727974)
print sw.user(1801443400)
print sw.socialgraph(1801443400)
#sw.auth()

