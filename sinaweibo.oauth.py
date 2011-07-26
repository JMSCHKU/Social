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
import socket
#from weibopy.auth import OAuthHandler, BasicAuthHandler
#from weibopy.api import API

class SinaWeiboOauth():
    sinaweiboOauth = mypass.getSinaWeiboOauth()
    pgconn = None
    toleranceNotToBeginning = 5 # in fetching timelines, break from loop when toleranceNotToBeginning consecutive statuses already exist in the DB
    toleranceNotToBeginningLong = 150 # for reposts
    max_gotall_count = 3
    api_wait_secs = 5
    max_api_misses = 6
    max_reposts_pages = max_comments_pages = 1000
    max_reposts_blanks = max_comments_blanks = 3
    max_reposts_tries = max_comments_tries = 3
    usage = "sinaweibo.oauth.py [id or file with ids] [primary opts] [sec opts]"
    comments_dir = "/var/data/sinaweibo/comments"
    reposts_dir = "/var/data/sinaweibo/reposts"
    verbose = False
    getall = False
    force_screenname = False
    checkonly = False
    doupdate = False

    def __init__(self):
	socket.setdefaulttimeout(300)

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
	    wkt_point = "POINT(" + str(lng) + " " + str(lat) + ")"
	    #print wkt_point
	    x["geo"] = "SRID=4326;" + wkt_point
	    '''
	    sql = "UPDATE %(table_name)s SET geo = ST_GeomFromText('%(wkt_point)s', 4326) WHERE id = %(id)d " % {"table_name": "sinaweibo", "wkt_point": wkt_point, "id": x["id"]}
	    try:
		self.pgconn.query(sql)
	    except:
		print sql
		print "geo error: " + wkt_point
	    '''
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

    def get_status(self, id, getUser=False, toDB=True):
	time_db = 0
	time_db_u = 0
	start_time_api = time.time()
	api_misses = 0
	while api_misses < self.max_api_misses:
	    try:
		status = self.api.get_status(id=id)
		break
	    except weibopy.error.WeibopError as e:
		print e.reason
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": e.reason }
		if e.reason.find("Error: target weibo does not exist!") > 0:
		    return { "msg": e.reason }
		time.sleep(self.api_wait_secs)
	time_api = time.time() - start_time_api
	row = self.status_to_row(status)
	r = dict()
	if toDB and not self.checkonly:
    	    start_time_db = time.time()
	    resp = self.toDB("sinaweibo", row, self.doupdate)
	    time_db += time.time() - start_time_db
	    r = resp
	    resp["time_db"] = time_db
	    if getUser:
    		timeline_user = self.getAtt(status, "user")
		start_time_db_u = time.time()
		u = self.user_to_row(timeline_user)
		resp_u = self.toDB("sinaweibo_users", u)
		time_db_u += time.time() - start_time_db_u
		r["time_db_u"] = time_db_u
	else:
	    print row
	r["time_api"] = time_api
	return r

    def user_timeline(self, user_id, count=200, page=1):
	start_time_api = time.time()
	api_misses = 0
	while api_misses < self.max_api_misses:
	    try:
		timeline = self.api.user_timeline(count=count, page=page, user_id=user_id)
		break
	    except httplib.IncompleteRead as h:
		print h
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": h }
		time.sleep(self.api_wait_secs)
	    except weibopy.error.WeibopError as e:
		print e.reason
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": e.reason }
		time.sleep(self.api_wait_secs)
	    except socket.error as e:
		print e
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": e.message }
		time.sleep(self.api_wait_secs)
	    '''
	    except ValueError as e:
		print user_id
		print e
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": e.message }
		time.sleep(self.api_wait_secs)
	    '''
	time_api = time.time() - start_time_api
	r = self.status_timeline(timeline, toBeginning=False)
	if "count" in r and r["count"] == 0:
	    if self.pgconn is None:
    		self.pgconn = mypass.getConn()
	    self.pgconn.query("UPDATE sinaweibo_users SET posts_updated = NOW() WHERE id = %d" % user_id)
	r["time_api"] = time_api
	r["page"] = page
	return r

    def reposts(self, status_id, count=200, page=1):
	already_exists_count = 0
	start_time_api = time.time()
	api_misses = 0
	while api_misses < self.max_api_misses:
	    try:
		timeline = self.api.repost_timeline(count=count, page=page, id=status_id)
		break
	    except weibopy.error.WeibopError as e:
		print e.reason
		api_misses += 1
		if api_misses == self.max_api_misses:
		    return { "msg": e.reason }
		if e.reason.find("Error: target weibo does not exist!") > 0:
		    return { "msg": e.reason }
		time.sleep(self.api_wait_secs)
	time_api = time.time() - start_time_api
	r = self.status_timeline(timeline, False)
	r["time_api"] = time_api
	r["page"] = page
	return r

    # common function to go through a timeline and optionally put in the DB
    def status_timeline(self, statuses, isSingleUser=True, toDB=True, toBeginning=True):
	already_exists_count = 0
	time_db = 0
	time_db_u = 0
	deleted_count = 0
	timeline_users_ids = list()
	toleranceNotToBeginningCount = 0
	newlyadded = 0
        for l in statuses:
	    x = self.status_to_row(l)
	    if toDB:
		start_time_db = time.time()
		# handle deleted statuses
		if "deleted" in x and x["deleted"] is not None and (x["deleted"] == "1" or x["deleted"] == 1 or x["deleted"] is True):
		    deleted_count += 1
		    if self.pgconn is None:
			self.pgconn = mypass.getConn()
		    try:
			sql_deleted = "UPDATE sinaweibo SET deleted = NOW() WHERE id = %d AND deleted IS NULL " % x["id"]
		    	res = self.pgconn.query(sql_deleted)
		    except pg.ProgrammingError, pg.InternalError:
			print self.pgconn.error
		    continue
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
			if isSingleUser:
			    if self.verbose:
				print "already exists, tolerance: " + str(toleranceNotToBeginningCount)
			    if toleranceNotToBeginningCount >= self.toleranceNotToBeginning:
				break
			else:
			    if toleranceNotToBeginningCount >= self.toleranceNotToBeginningLong:
				break
		else:
		    newlyadded += 1
		    if not toBeginning:
			toleranceNotToBeginningCount = 0
	    else:
		print x
	r = { "count": len(statuses), "deleted_count": deleted_count }
	if isSingleUser and toDB and len(statuses) > 0:
	    u = self.user_to_row(self.getAtt(statuses[0], "user"))
	    u["last_post_date"] = self.getAtt(statuses[0], "created_at").strftime("%Y-%m-%d %H:%M:%S")
	    u["posts_updated"] = "NOW()"
	    start_time_db_u = time.time()
	    resp_u = self.toDB("sinaweibo_users", u, doupdate=True)
	    #print resp_u
	    time_db_u += time.time() - start_time_db_u
	    r["user_id"] = u["id"]
	if toDB:
	    if toBeginning:
		r["already_exists_count"] = already_exists_count 
	    r["newly_added"] = newlyadded
	    r["time_db"] = time_db
	    r["time_db_u"] = time_db_u
	return r

    def comments(self, status_id, count=200, page=1, toDB=True, toBeginning=True):
	already_exists_count = 0
	start_time_api = time.time()
	api_misses = 0
	while api_misses < self.max_api_misses:
	    try:
		comments = self.api.comments(id=status_id, count=count, page=page)
		break
	    except weibopy.error.WeibopError as e:
		print e.reason
		api_misses += 1
		if api_misses == self.max_api_misses:
		    return { "msg": e.reason }
		time.sleep(self.api_wait_secs)
		continue
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
	try:
	    if screen_name is not None:
		user = self.api.get_user(screen_name=screen_name)
	    else:
		user = self.api.get_user(user_id=user_id)
	except weibopy.error.WeibopError as e:
	    if e.reason.find("User does not exists") > 0:
		if self.pgconn is None:
		    self.pgconn = mypass.getConn()
		try:
		    if not self.force_screenname and not user_id is None:
			sql_deleted = "UPDATE sinaweibo_users SET deleted = NOW() WHERE id = %d AND deleted IS NULL " % user_id
			res = self.pgconn.query(sql_deleted)
		except pg.ProgrammingError, pg.InternalError:
		    print self.pgconn.error
	    return { "msg": e.reason }
	time_api = time.time() - start_time_api
	time_db = 0
	x = self.user_to_row(user)
	if toDB:
	    start_time_db = time.time()
	    resp = self.toDB("sinaweibo_users", x, doupdate=True)
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

    def toDB(self, tablename, data, doupdate=False, updatefirst=False):
	if self.pgconn is None:
	    self.pgconn = mypass.getConn()
	resp = { "success": False, "already_exists": False }
	if updatefirst:
	    if doupdate:
		try:
		    r = self.pgconn.update(tablename, data)
		    resp["success"] = True
		except pg.DatabaseError:#, pg.ProgrammingError, pg.InternalError:
		    if self.pgconn.error.find('No such record in') > 0:
			try:
			    r = self.pgconn.insert(tablename, data)
			    resp["success"] = True
			except:
			    if self.pgconn.error.find('duplicate key value violates unique constraint') > 0:
				resp["already_exists"] = True
	    else:
		try:
		    print data
		    r = self.pgconn.insert(tablename, data)
		    resp["success"] = True
		except:
		    if self.pgconn.error.find('duplicate key value violates unique constraint') > 0:
			resp["already_exists"] = True
	else:
	    try:
		self.pgconn.insert(tablename, data)
		resp["success"] = True
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
    
    # Sends from command-line to the appropriate function
    def dispatch(self, opt, id, output_counts=False):
	if opt == 1: # user timeline
	    out = self.user_timeline(id)
	    if "count" in out and out["count"] == 0: # see if the user was just deleted
		out_user = self.user(id)
	elif opt == 2: # user
	    if self.force_screenname:
		out = self.user(None, id)
	    else:
		out = self.user(id)
	elif opt == 3: # friends
	    out = self.socialgraph(id, "friends")
	    if out["count"] == 5000:
		out = self.socialgraph(id, "friends", 4999)
	elif opt == 4: # followers
	    out = self.socialgraph(id, "followers")
	    if out["count"] == 5000:
		out = self.socialgraph(id, "followers", 4999)
	elif opt == 7: # reposts
	    blanks_count = 0
	    gotall_count = 0
	    for i in range(self.max_reposts_pages):
		items_count = 0
		misses_count = 0
		trial = 0
		while items_count == 0 and misses_count <= self.max_reposts_tries:
		    time.sleep(5)
		    out = self.reposts(id, 200, i+1)
		    if not "count" in out:
			misses_count += 1
			rls = self.api.rate_limit_status()
			ratelimstatus = { "remaining_hits": self.getAtt(rls, "remaining_hits"), "hourly_limit": self.getAtt(rls, "hourly_limit"), "reset_time_in_seconds": self.getAtt(rls, "reset_time_in_seconds"), "reset_time": self.getAtt(rls, "reset_time") }
			if self.verbose:
			    print ratelimstatus
			continue
		    elif out["count"] == 0:
			out["msg"] = "Too many blanks: probably reached the end"
			blanks_count += 1
			gotall_count += 1
			break
		    else:
			blanks_count = 0
		    items_count = out["count"]
		if self.verbose:
		    out["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		    print out
		if misses_count >= self.max_reposts_tries:
		    print out["msg"]
		    time.sleep(60)
		    break
		elif blanks_count >= self.max_reposts_blanks:
		    print out["msg"]
		    break
		if items_count == out["already_exists_count"]: # already got everything
		    gotall_count += 1
		    #continue # still continue
		    if not self.getall and gotall_count >= self.max_gotall_count:
			out["msg"] = "Already full " + str(self.max_gotall_count) + " times: we're breaking here"
			break
		    continue
	    if output_counts:
		if self.pgconn is None:
		    self.pgconn = mypass.getConn()
		sql_count = "SELECT COUNT(*) FROM sinaweibo WHERE retweeted_status = %d " % id
		res_count = self.pgconn.query(sql_count).getresult()
		fo = open(self.reposts_dir + "/counts/" + str(id), "w")
		fo.write(str(res_count[0][0]))
		fo.close()
	elif opt == 8: # comments
	    blanks_count = 0
	    gotall_count = 0
	    for i in range(self.max_comments_pages):
		items_count = 0
		misses_count = 0
		trial = 0
		while items_count == 0 and misses_count <= self.max_comments_tries:
		    time.sleep(5)
		    out = self.comments(id, 200, i+1)
		    if not "count" in out:
			misses_count += 1
			rls = self.api.rate_limit_status()
			ratelimstatus = { "remaining_hits": self.getAtt(rls, "remaining_hits"), "hourly_limit": self.getAtt(rls, "hourly_limit"), "reset_time_in_seconds": self.getAtt(rls, "reset_time_in_seconds"), "reset_time": self.getAtt(rls, "reset_time") }
			if self.verbose:
			    print ratelimstatus
			continue
		    elif out["count"] == 0:
			out["msg"] = "Too many blanks: probably reached the end"
			blanks_count += 1
			gotall_count += 1
			break
		    else:
			blanks_count = 0
		    items_count = out["count"]
		if self.verbose:
		    out["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		    print out
		if misses_count >= self.max_comments_tries:
		    print out["msg"]
		    time.sleep(60)
		    break
		elif blanks_count >= self.max_comments_blanks:
		    print out["msg"]
		    break
		if items_count == out["already_exists_count"]: # already got everything
		    gotall_count += 1
		    if not self.getall and gotall_count >= self.max_gotall_count:
			break
		    continue #break
	    if output_counts:
		if self.pgconn is None:
		    self.pgconn = mypass.getConn()
		sql_count = "SELECT COUNT(*) FROM sinaweibo_comments WHERE status_id = %d " % id
		res_count = self.pgconn.query(sql_count).getresult()
		fo = open(self.comments_dir + "/counts/" + str(id), "w")
		fo.write(str(res_count[0][0]))
		fo.close()
	elif opt == 9: # single status
	    out = self.get_status(id)
	else:
	    out = None
	return out


if __name__ == "__main__":
    sw = SinaWeiboOauth()
    output_counts = False
    
    # prepare args
    if len(sys.argv) <= 2:
	print sw.usage
	sys.exit()
    else:
	try:
	    id = long(sys.argv[1])
	except ValueError:
	    id = 0
	    fname = str(sys.argv[1])
    # primary option
    if len(sys.argv) > 2:
	opt = sys.argv[2]
	if opt == "-ut" or opt == "--user-timeline":
	    opt = 1 # user timeline
	elif opt == "-u" or opt == "--users":
	    opt = 2 # users
	elif opt == "-fr" or opt == "--friends":
	    opt = 3 # friends
	elif opt == "-fl" or opt == "--followers":
	    opt = 4 # followers
	elif opt == "-rp" or opt == "--reposts":
	    opt = 7 # reposts
	elif opt == "-cm" or opt == "--comments":
	    opt = 8 # comments
	elif opt == "-ss" or opt == "--single-status":
	    opt = 9 # single status
	else:
	    print self.usage # single status
	    sys.exit()
    # secondary options
    for i in range(3,len(sys.argv)):
	if sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
    	    sw.verbose = True
	elif sys.argv[i] == "-c" or sys.argv[i] == "--counts":
    	    output_counts = True
	elif sys.argv[i] == "-a" or sys.argv[i] == "--get-all":
    	    sw.getall = True
	elif sys.argv[i] == "-fs" or sys.argv[i] == "--force-screenname":
    	    sw.force_screenname = True
	    fname = str(sys.argv[1])
	elif sys.argv[i] == "-co" or sys.argv[i] == "--check-only":
	    sw.checkonly = True
	elif sys.argv[i] == "-u" or sys.argv[i] == "--update":
    	    sw.doupdate = True

    # bind token and set the api
    sw.setToken(sw.sinaweiboOauth["oauth_token"], sw.sinaweiboOauth["oauth_token_secret"]) 

    # dispatch
    if sw.force_screenname:
	out = sw.dispatch(opt, fname, output_counts)
	out = [out]
    elif id > 0:
	out = sw.dispatch(opt, id, output_counts)
	out["id"] = id
	out = [out] # put in an array for consistency with list of ids
    else:
	try:
	    f = open(fname, "r")
	except IOError:
	    print sw.usage
	    sys.exit()
	out = list()
	for l in f:
	    try:
		id = long(l) # try with the whole line
	    except ValueError:
		try:
		    id = long(l.split(",")[0]) # try on the first comma-sep value
		except ValueError:
		    continue
	    thisout = sw.dispatch(opt, id, output_counts)
	    thisout["id"] = id
	    out.append(thisout)
    output = { "data": out, "opt": opt, "count": len(out), "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") }
    if sw.verbose:
	print output

    #sw.auth()
    #sw.setToken("24910039392f0acf7b83b8cb91ee9191", "1363bae989c232bf5db6aefb3e6460c7")
    #print sw.user_timeline(1801443400)
    #print sw.comments(10741815655)
    #print sw.reposts(10713727974)
    #print sw.user(1801443400)
    #print sw.socialgraph(1801443400)
    #sw.auth()

