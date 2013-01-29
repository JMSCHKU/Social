#!/usr/bin/env python
# -*- coding: utf-8 -*-

## using APIClient from https://github.com/michaelliao/sinaweibopy

import weibo
import mypass
import sys
import pg
import httplib
import time
import datetime
import string
import csv
import types
import argparse
import re
import os
import socket

#import lucene
#import sinaweibolucene

class API():
    sinaweiboOauth = mypass.getSinaWeiboOauth2(0)
    nb_api_keys = sinaweiboOauth["nb_api_keys"]
    max_api_misses = 6
    pgconn = None
    toleranceNotToBeginning = 5 # in fetching timelines, break from loop when toleranceNotToBeginning consecutive statuses already exist in the DB
    toleranceNotToBeginningLong = 150 # for reposts
    max_gotall_count = 3
    api_wait_secs = 5
    api_long_wait_secs = 3600
    max_api_misses_half = 3
    max_api_misses = 3 ## reduced from 6
    max_reposts_pages = max_comments_pages = 1000
    max_reposts_blanks = max_comments_blanks = 3
    max_reposts_tries = max_comments_tries = 3
    rp_dir = "/var/data/sinaweibo/rp"
    comments_dir = "/var/data/sinaweibo/comments"
    reposts_dir = "/var/data/sinaweibo/reposts"
    timelines_dir = "/var/data/sinaweibo/timelines"
    timeline_ids = list()
    verbose = 0
    getall = False
    force_screenname = False
    checkonly = False
    doupdate = False
    saveRP = False
    rt = False # Don't store the retweet
    index = False
    indexer = None
    doublecheck = False # If we get a blank timeline, it may just be an error, so we log it
    user = False
    cliparser = argparse.ArgumentParser(description="Sina Weibo API to DB tool")
    id = None

    def __init__(self):
	self.setClient()
	self.setToken(self.sinaweiboOauth['access_token'], self.sinaweiboOauth['expires_in'])
	self.initParser()
	out = self.dispatch()
	out["app_key"] = self.sinaweiboOauth['app_key']
	out["keyindex"] = self.sinaweiboOauth['keyindex']
	if self.verbose > 0:
	    print out

    def setClient(self):
        self.api2 = weibo.APIClient(app_key=self.sinaweiboOauth['app_key'], app_secret=self.sinaweiboOauth['app_secret'], redirect_uri=self.sinaweiboOauth['redirect_uri'])

    def setToken(self, access_token, expires_in):
        self.api2.set_access_token(access_token, expires_in)
    
    def reqToken(self, access):
        self.api2.set_access_token(self.sinaweiboOauth['access_token'], self.sinaweiboOauth['expires_in'])

    def changeToken(self):
	keyindex = (self.sinaweiboOauth["keyindex"] + 1) % self.nb_api_keys
	if self.sinaweiboOauth["keyindex"] + 1 > self.nb_api_keys:
	    time.sleep(self.api_long_wait_secs)
	self.sinaweiboOauth = mypass.getSinaWeiboOauth2(keyindex)
	self.setClient()
	self.setToken(self.sinaweiboOauth['access_token'], self.sinaweiboOauth['expires_in'])
	if self.verbose > 1:
	    print "Changing key: " + self.sinaweiboOauth['app_key']

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

    def fixdate(self, textdate):
        '''
        fix the date(string) returned from Sina to the standard format 
        '''
        textdate = re.sub(r' \+....', '', textdate) # kill the +0800, not supported by strptime
        datedt = datetime.datetime.strptime(textdate, "%a %b %d %H:%M:%S %Y")
        return datedt.strftime("%Y-%m-%d %H:%M:%S")
    #def get_rateLimit(self):

    def get_apistatus(self):
        ratelimit = self.api2.account.rate_limit_status.get()
        print ratelimit
        
    def get_status(self):
        time_db = 0
        time_db_u = 0
        start_time_api = time.time()
        api_misses = 0
        while api_misses < self.max_api_misses:
            try:
                status = self.api2.statuses.show.get(id=self.id)
                break
            except weibo.APIError as e: ## Need more exception handling, and warned by > Python 2.6.
		if self.verbose > 0:
		    print e
		if e is not None and ("out of rate limit" in str(e).lower()):
		    self.changeToken()			
		    api_misses += 1
                if api_misses >= self.max_api_misses:
                    return { "id": self.id, "err_msg": e } ## aka toxicbar
                if e is not None and ("target weibo does not exist" in str(e).lower() or "permission denied" in str(e).lower()):
		    out = { 'id': self.id, "error_msg": str(e).lower(), "deleted": True, "permission_denied": False }
                    permission_denied = False
                    if ("permission denied" in str(e).lower()):
                        permission_denied = True
		    try:
			if self.pgconn is None:
		    	    self.pgconn = mypass.getConn()
			permission_sql = ""
			if "permission denied" in str(e).lower():
			    permission_sql = ", permission_denied = true"
			    out["permission_denied"] = True
			sql_deleted = "UPDATE rp_sinaweibo SET deleted = NOW() %(permission)s WHERE id = %(id)d AND deleted IS NULL " % { "id": self.id, "permission": permission_sql }
			if self.verbose > 0:
			    print "deleted %d " % self.id
		    	res = self.pgconn.query(sql_deleted)
			sql_status = "SELECT * FROM rp_sinaweibo WHERE id = %(id)d " % { "id": self.id }
			res_status = self.pgconn.query(sql_status).dictresult()
			out["deleted"] = True
			if len(res_status) > 0:
			    out["user_id"] = res_status[0]["user_id"]
			if self.verbose > 1:
			    out["status"] = res_status[0]
			    out["sql"] = sql_deleted
			return out
		    except pg.ProgrammingError, pg.InternalError:
			print self.pgconn.error
                time.sleep(self.api_wait_secs * 1)
        time_api = time.time() - start_time_api
        # status is just a glorified dict, not an object like weibopy2
        # So don't need to use getAtt
        row = self.status_to_row(status) 
	row_rt = None
	if "rt" in row:
	    row_rt = row["rt"]
    	r = dict()
	if "deleted" in row and row["deleted"] is not None and (row["deleted"] == "1" or row["deleted"] == 1 or row["deleted"] is True):
	    if self.pgconn is None:
		self.pgconn = mypass.getConn()
	    sql_deleted = "UPDATE rp_sinaweibo SET deleted = NOW() WHERE id = %(id)d AND deleted IS NULL " % { "id": id }
    	    res = self.pgconn.query(sql_deleted)
	    sql_status = "SELECT * FROM rp_sinaweibo WHERE id = %(id)d " % { "id": id }
    	    res_status = self.pgconn.query(sql_status).dictresult()
	    out = { "msg": "row deleted", "deleted": True }
	    if len(res_status) > 0:
		out["user_id"] = res_status[0]["user_id"]
	    return out
	if not self.checkonly:
    	    start_time_db = time.time()
	    tablename = self.getRangePartitionByDate(row["created_at"])
    	    resp = self.toDB(tablename, row, self.doupdate)
	    if row_rt is not None and self.rt:
		tablename_rt = self.getRangePartitionByDate(row_rt["created_at"])
		resp_rt = self.toDB(tablename_rt, row_rt, self.doupdate)
	    time_db += time.time() - start_time_db
	    r = resp
	    resp["time_db"] = time_db
	    if self.user:
		# Also store the user
		timeline_user = self.getAtt(status, "user")
		start_time_db_u = time.time()
		u = self.user_to_row(timeline_user)
		resp_u = self.toDB("sinaweibo_users", u)
		time_db_u += time.time() - start_time_db_u
		r["time_db_u"] = time_db_u
		r["user"] = resp_u
	if self.verbose > 1:
	    print row
	return row

    def get_usertimeline(self, count=200, page=1):
        start_time_api = time.time()
        api_misses = 0
        while api_misses < self.max_api_misses:
            try:
                timeline = self.api2.statuses.user_timeline.get(uid=self.id, count=count, page=page)
                break
	    except httplib.IncompleteRead as h:
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": h }
		time.sleep(self.api_wait_secs)
	    except weibo.APIError as e:
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": e }
		time.sleep(self.api_wait_secs)
		if e is not None and ("out of rate limit" in str(e).lower()):
		    self.changeToken()
	    except socket.error as e:
		api_misses += 1
		if api_misses >= self.max_api_misses:
		    return { "msg": e }
		time.sleep(self.api_wait_secs)
            except Exception as e:
		if self.verbose > 0:
		    print e
	    	api_misses += 1
                if api_misses >= self.max_api_misses:
                    return { "id": self.id, "err_msg": e }
	time_api = time.time() - start_time_api
	r = self.status_timeline(timeline["statuses"])
	if "count" in r and r["count"] == 0:
	    if self.doublecheck is not False:
		try:
		    fdc = open(self.doublecheck, "a")
		    fdc.write("\n" + str(user_id))
		    fdc.close()
		    print "wrote to %s " + self.doublecheck
		except:
		    pass
	# save timeline ids
	if len(self.timeline_ids) > 0:
	    if self.verbose > 0:
		print self.timeline_ids
	    umask = os.umask(0)
	    fo = open(self.timelines_dir + "/current/" + str(self.id), "w")
	    for timeline_id in self.timeline_ids:
		fo.write(str(timeline_id)+"\n")
	    fo.close()
	    os.umask(umask)
	r["time_api"] = time_api
	r["page"] = page
	return r

    def get_userinfo(self):
        start_time_api = time.time()
        api_misses = 0
        while api_misses < self.max_api_misses:
            try:
                userinfo = self.api2.users.show.get(uid=self.id)
                break
            except Exception as e:
       		if self.verbose > 0:
		    print e
		if e is not None and ("out of rate limit" in str(e).lower()):
		    self.changeToken()			
	    	api_misses += 1
                if api_misses >= self.max_api_misses:
                    return { "id": id, "err_msg": e }
        return userinfo

    def status_timeline(self, statuses, isSingleUser=True, toBeginning=True):
	already_exists_count = 0
	time_db = 0
	time_db_u = 0
	if self.index:
	    time_index = 0
	deleted_count = 0
	timeline_users_ids = list()
	toleranceNotToBeginningCount = 0
	newlyadded = 0
        for l in statuses:
	    x = self.status_to_row(l)
	    x_rt = None
	    if "rt" in x:
		x_rt = x["rt"]
	    start_time_db = time.time()
	    if ("user_id" not in x or ("user_id" in x and x["user_id"] is None)) and self.id is not None:
		x["user_id"] = self.id
	    # handle deleted statuses
	    if "deleted" in x and x["deleted"] is not None and (x["deleted"] == "1" or x["deleted"] == 1 or x["deleted"] is True):
		deleted_count += 1
		if self.pgconn is None:
		    self.pgconn = mypass.getConn()
		try:
		    sql_deleted = "UPDATE rp_sinaweibo SET deleted = NOW() WHERE id = %(id)d AND deleted IS NULL " % { "id": x["id"] }
		    res = self.pgconn.query(sql_deleted)
		except pg.ProgrammingError, pg.InternalError:
		    print self.pgconn.error
		continue
	    tablename = self.getRangePartitionByDate(x["created_at"])
	    #tablename = "rp_sinaweibo"
	    resp = self.toDB(tablename, x)
	    if x_rt is not None and self.rt:
		tablename_rt = self.getRangePartitionByDate(x_rt["created_at"])
		resp_rt = self.toDB(tablename_rt, x_rt, self.doupdate)
	    time_db += time.time() - start_time_db
	    if not resp["already_exists"] and resp["success"] and not isSingleUser:
		timeline_user = self.user_to_row(l["user"])
		timeline_user_id = timeline_user["id"]
		if self.verbose > 1:
		    print resp
		if not timeline_user_id in timeline_users_ids:
		    start_time_db_u = time.time()
		    u = self.user_to_row(timeline_user)
		    resp_u = self.toDB("sinaweibo_users", u, doupdate=True)
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
		if self.index: # index if the row doesn't already exist
		    time_index_start = time.time()
		    try:
			t = time.strptime(x["created_at"],"%Y-%m-%d %H:%M:%S")
			created_at_secs = int(time.mktime(t))
			self.indexer.indexWeibo(x["id"], x["text"], x["user_id"], created_at_secs)
		    except Exception as e:
			print e
		    time_index += time.time() - time_index_start
	    if self.verbose > 1:
		print x
	r = { "count": len(statuses), "deleted_count": deleted_count }
	if isSingleUser and len(statuses) > 0:
	    u = self.user_to_row(statuses[0]["user"])
	    u["last_post_date"] = statuses[0]["created_at"]
	    u["posts_updated"] = "NOW()"
	    start_time_db_u = time.time()
	    resp_u = self.toDB("sinaweibo_users", u, doupdate=True)
	    if self.verbose > 0:
		print resp_u
	    time_db_u += time.time() - start_time_db_u
	    r["user_id"] = u["id"]
	if isSingleUser and len(statuses) > 0:
	    for s in statuses:
		try:
		    self.timeline_ids.append(s["id"])
		except:
		    pass
	if toBeginning:
	    r["already_exists_count"] = already_exists_count 
	r["newly_added"] = newlyadded
	r["time_db"] = time_db
	r["time_db_u"] = time_db_u
	if self.index:
	    r["time_index"] = time_index
	return r

    def status_to_row(self, status):
        x = dict()
        x["created_at"] = self.fixdate(status["created_at"])
        for a in ["text", "source", "location", "thumbnail_pic", "bmiddle_pic", "original_pic", "screen_name", "in_reply_to_screen_name"]:
            try:
                att = status[a]
            except:
                att = None
            try:
                x[a] = att.encode("utf8")
            except:
                x[a] = att
        for a in ["id", "in_reply_to_user_id", "in_reply_to_status_id", "truncated", "reposts_count", "comments_count", "attitudes_count", "mlevel", "deleted"]:
            try:
                x[a] = status[a]
            except:
                x[a] = None
    	x['user_id'] = status['user']['id']
        try:
            x['retweeted_status'] = status['retweeted_status']['id']
            if self.rt:
                rt_dict = status['retweeted_status']
                if rt_dict['created_at'] is not None:
                    x['rt'] = self.status_to_row(rt_dict)
        except:
            rts = None # This message is original
        try:
            x['retweeted_status_user_id'] = status['retweeted_status']['user']['id']
        except:
            pass
        try:
            x['screen_name'] = status['user']['screen_name'].encode("utf-8")
        except:
            pass
        try:
            geo = status['geo']
            coord = geo["coordinates"]
        except:
            geo = None
        if geo is not None and coord is not None and len(coord) >0:
            lat = coord[0]
            lng = coord[1]
            wkt_point = "POINT(" + str(lng) + " " + str(lat) + ")"
	    #print wkt_point
	    x["geo"] = "SRID=4326;" + wkt_point
	return x

    def user_to_row(self, userinfo):
	x = dict()
	try:
            x["created_at"] = self.fixdate(userinfo["created_at"])
	except:
	    x["created_at"] = None
	x["retrieved"] = "NOW()"
	for a in ["name", "screen_name", "location", "description", "profile_image_url", "url", "avatar_large", "verified_reason"]:
	    try:
		att = userinfo[a]
		x[a] = att.encode("utf8")
	    except:
		x[a] = None
	for a in ["id", "province", "city", "domain", "gender", "followers_count", "friends_count", "favourites_count", \
"time_zone", "profile_background_image_url", "profile_use_background_image", "allow_all_act_msg", "geo_enabled", \
"verified", "following", "statuses_count", "allow_all_comment", "bi_followers_count", "deleted", "verified_type", "lang", "online_status"]:
            try:
                x[a] = userinfo[a]
            except:
                x[a] = None
	return x

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
		    #print data
		    r = self.pgconn.insert(tablename, data)
		    resp["success"] = True
		except:
		    if self.pgconn.error.find('duplicate key value violates unique constraint') > 0:
			resp["already_exists"] = True
	else:
	    try:
		#print data
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
			resp["reason"] = self.pgconn.error
			pass

	#pgconn.close()
	return resp
    
    def dispatch(self):
    	if self.opt == 1:
            out = self.get_usertimeline()
        elif self.opt == 9:
            out = self.get_status()
        else:
            out = None
        return out

    class ParseAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
	    #print '%r %r %r' % (namespace, values, option_string)
	    if option_string == "-ut" or option_string == "--user-timeline":
		setattr(namespace, "opt", 1)
	    if option_string == "-ui" or option_string == "--user-info":
		setattr(namespace, "opt", 2)
	    if option_string == "-ss" or option_string == "--single-status":
		setattr(namespace, "opt", 9)

    def initParser(self):
	self.cliparser.add_argument("id", metavar="ID", type=int, help="an ID")
	self.cliparser.add_argument("--single-status", "-ss", action=self.ParseAction, nargs=0)
	self.cliparser.add_argument("--user-timeline", "-ut", action=self.ParseAction, nargs=0)
	self.cliparser.add_argument("--user-info", "-ui", action=self.ParseAction, nargs=0)
	self.cliparser.add_argument("--user", "-u", action=self.ParseAction, nargs=0)
	self.cliparser.add_argument("--retweet", "-rt", action="store_true")
	self.cliparser.add_argument('--verbose', '-v', action='count')
	args = self.cliparser.parse_args()
	self.id = args.id
	self.opt = args.opt
	self.rt = args.retweet
	if args.verbose is not None:
	    self.verbose = args.verbose
	if args.user is not None:
	    self.user = True
	if self.verbose > 1:
	    print args

    def saveRangePartitionByIdDate(self, id, date):
	isocal = date.isocalendar()
	f = open(self.rp_dir + "/ids/" + str(id), "w")
	f.write(str(isocal[0]) + "," + str(isocal[1]))
	f.close()

    def waitRateLimit(self):
	rls = self.api2.rate_limit_status()
	ratelimstatus = { "remaining_hits": self.getAtt(rls, "remaining_hits"), "hourly_limit": self.getAtt(rls, "hourly_limit"), "reset_time_in_seconds": self.getAtt(rls, "reset_time_in_seconds"), "reset_time": self.getAtt(rls, "reset_time") }
	reset_time = int(self.getAtt(rls, "reset_time_in_seconds")) + self.api_wait_secs
	if self.verbose:
	    print "Reset time in %(secs)d seconds (now: %(now)s) " % { "secs": reset_time, "now": datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")}
	if reset_time > 2700 and reset_time < 3600:
	    time.sleep(120)
	elif reset_time > 120:
	    time.sleep(reset_time + 30)
	else:
	    time.sleep(self.api_wait_secs * 5)

    def getRangePartitionByDate(self, dt_created_at):
	if type(dt_created_at) is types.StringType:
	    dt_created_at = datetime.datetime.strptime(dt_created_at, "%Y-%m-%d %H:%M:%S")
	isocal = dt_created_at.isocalendar()
	return "rp_sinaweibo_y" + str(isocal[0]) + "w" + str(isocal[1])

if __name__ == "__main__":
    api = API()

