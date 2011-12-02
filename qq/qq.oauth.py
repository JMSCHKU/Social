#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import mypass
import urllib
import httplib2
import time
import string
import json
import types

import qweiboclient

class qq():

    qqkeys = None
    api_wait_secs = 2
    pgconn = None
    http = None
    verbose = False
    time_api = 0
    time_db = 0
    time_db_u = 0
    time_db_entities = 0
    newlyadded = 0
    already_exists_count = 0
    entities = False
    doupdate = False
    usage = "qq.oauth.py [id or file with ids] [primary opts] [sec opts]"
    qqclient = None
    MAX_PAGES_FRIENDS = 50
    MAX_PAGES_TIMELINES = 50
    toleranceNotToBeginning = 10

    def __init__(self):
	self.qqkeys = mypass.getQQKey()
	self.pgconn = mypass.getConn()
	self.http = httplib2.Http()
	self.qqclient = qweiboclient.QQWeiboClient(self.qqkeys["consumer_key"], self.qqkeys["consumer_secret"])
	self.qqclient.setAccessToken(self.qqkeys["oauth_token"], self.qqkeys["oauth_token_secret"])

    def get_status(self, id):
	start_time_api = time.time()
	api_misses = 0
	t = self.qqclient.t(id=id)
	return t

    def get_user(self, name):
	start_time_api = time.time()
	api_misses = 0
	user = self.qqclient.user(name=name)
	return user

    def user_timeline(self, name):
	r = dict()	
	start_time_api = time.time()
	api_misses = 0
	loops = 0
	pagetime = 0
	while True and loops < self.MAX_PAGES_TIMELINES and (loops == 0 or pagetime != 0):
	    start_time_api = time.time()
	    user_timeline = self.qqclient.userTimeline(name=name, pagetime=pagetime)
	    self.time_api += time.time() - start_time_api
	    if "info" in user_timeline:
		r = self.status_timeline(user_timeline["info"])
		if "nextpagetime" in r:
		    pagetime = r["nextpagetime"]
		else:
		    break
	    loops += 1
	user_timeline["loops"] = loops
	user_timeline["pagetime"] = pagetime
	user_timeline["time_api"] = self.time_api
	return user_timeline

    def status(self, status):
	if "video" in status and status["video"] is not None:
	    for a in ["picurl", "player", "realurl", "shorturl", "title"]:
		if a in status["video"]:
		    x["video_" + a] = status["video"][a]
	if "music" in status and status["music"] is not None:
	    for a in ["author", "url", "title"]:
		if a in status["music"]:
		    status["music_" + a] = status["music_"][a]
	if "image" in status and status["image"] is not None and len(status["image"]) > 0:
	    images_concat = ""
	    first = True
	    for x in status["image"]:
		if first:
		    first = False
		else:
		    images_concat += ","
		if "," in x:
		    images_concat += '"%s"' % x
		else:
		    images_concat += x
	    status["image"] = "{%s}" % images_concat
	if "geo" in status and "geo" is not None and type(status["geo"]) is types.DictType:
	    lat = status["geo"][0]
	    lng = status["geo"][1]
	    wkt_point = "POINT(" + str(lng) + " " + str(lat) + ")"
	    print wkt_point
	    #status["geo"] = "SRID=4326;" + wkt_point
	for a in ["text","origtext","name","nick","from","location","video_title","music_author","music_title"]:
	    if a in status and status[a] is not None:
		try:
		    if len(status[a]) <= 0:
			status[a] = None
		    else:
			status[a] = status[a].encode("utf8")
		except:
	    	    pass
	out = self.toDB("qqweibo", status)#, doupdate=True)
	return out
 
    def user(self, user):
	for a in ["country_code","province_code","city_code","birth_year","birth_month","birth_day"]:
	    if a in user and user[a] is not None:
		try:
		    user[a] = int(user[a])
		except:
		    pass
	for a in ["name","nick","location","introduction","verifyinfo","email"]:
	    if a in user and user[a] is not None:
    		try:
	    	    if len(user[a]) <= 0:
	    		user[a] = None
	    	    else:
			user[a] = user[a].encode("utf8")
		except:
	    	    pass
	'''
	if "tweet" in user and user["tweet"] is not None:
	    for x in user["tweet"]:
		for a in ["name","nick"]:
		    if a in user and user[a] is not None:
			x[a] = user[a]
		self.status(x)
	'''
	if "tag" in user and user["tag"] is not None:
	    for x in user["tag"]:
		self.tag(x)
		if "name" in user:
		    self.usertag(user["name"], x["id"])
	if "edu" in user and user["edu"] is not None:
	    for x in user["edu"]:
		self.edu(x)
		if "name" in user:
		    self.useredu(user["name"], x["id"])
	out = self.toDB("qqweibo_users", user, doupdate=True)
	return out

    def tag(self, tag):
	for a in ["name"]:
	    if a in tag and tag[a] is not None:
		try:
		    tag[a] = tag[a].encode("utf8")
		except:
		    pass
	self.toDB("qqweibo_tags", tag)

    def usertag(self, user_name, tid):
	tag = { "user_name": user_name, "tag_id": tid }
	self.toDB("qqweibo_usertags", tag)

    def edu(self, edu):
	for a in ["name"]:
	    if a in edu and edu[a] is not None:
		try:
		    edu[a] = edu[a].encode("utf8")
		except:
		    pass
	self.toDB("qqweibo_edus", edu)

    def useredu(self, user_name, eid):
	edu = { "user_name": user_name, "edu_id": eid }
	self.toDB("qqweibo_useredus", edu)

    def status_timeline(self, statuses):
	toleranceNotToBeginningCount = 0
	r_list = list()
	nextpagetime = 0
        for status in statuses:
	    r = self.status(status)
	    r_list.append(r)
	    if "timestamp" in status:
		nextpagetime = status["timestamp"]
	    if r["already_exists"]:
		toleranceNotToBeginningCount += 1
	    if toleranceNotToBeginningCount >= self.toleranceNotToBeginning:
		break
	r = dict()
	r["nextpagetime"] = nextpagetime
	r["statuses_resp"] = r_list
	return r

    def search_statuses(self, query):
	r = self.qqclient.search_t(keyword=query)
	return r

    def search_users(self, query):
	r = self.qqclient.search_user(keyword=query)
	return r

    def friends(self, name, rel="idol", reqnum=30, startindex=0):
	#r = self.qqclient.friends(name=name, rel=rel, reqnum=30, startindex=startindex)
	loops = 0
	tablename = "qqweibo_friends"
	if rel.startswith("fans"):
	    tablename = "qqweibo_followers"
	r_list = list()
	while True and loops < self.MAX_PAGES_FRIENDS:
	    try:
		r = self.qqclient.friends(name=name, rel=rel, reqnum=30, startindex=startindex)
	    except:
		loops += 1
		continue
	    if "info" in r and r["info"] is not None:
		for u in r["info"]:
		    self.user(u)
		    udb = dict()
		    udb["source_id"] = name
		    try:
			udb["target_id"] = u["name"].encode("utf8")
		    except:
			udb["target_id"] = u["name"]
		    r_row = self.toDB(tablename, udb)
		    r_list.append(r_row)
	    else:
		print "Loops performed: %d" % loops
		break
	    loops += 1
	    startindex += 30
    	    if r is None:
		break
	return r

    def toDB(self, tablename, data, doupdate=False, updatefirst=False):
	if self.pgconn is None:
	    self.pgconn = mypass.getConn()
	resp = { "success": False, "already_exists": False }
	#r = self.pgconn.insert(tablename, data)
	r = dict()
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
		r = self.pgconn.insert(tablename, data)
    		resp["success"] = True
	    except pg.ProgrammingError, pg.InternalError:
		if self.pgconn.error.find('duplicate key value violates unique constraint') > 0:
		    resp["already_exists"] = True
		    try:
			if doupdate:
			    r = self.pgconn.update(tablename, data)
			    resp["success"] = True
		    except:
			resp["reason"] = self.pgconn.error
			pass
	if self.verbose:
	    resp["r"] = r
	return resp

    # Sends from command-line to the appropriate function
    def dispatch(self, opt, id):
	if opt == 1: # user timeline
	    out = self.user_timeline(id)
	    '''
	    if "count" in out and out["count"] == 0: # see if the user was just deleted
		out_user = self.user(id)
	    '''
	elif opt == 2: # user
	    user = self.get_user(id)
	    out = self.user(user)
	elif opt == 9: # single status
	    status = self.get_status(id)
	    out = self.status(status)
	elif opt == 3: # friends
	    out = self.friends(id, "idol")
	elif opt == 4: # followers
	    out = self.friends(id, "fans")
	elif opt == 10: # search posts
	    out = self.search_statuses(id) # id is actually the query string
	elif opt == 11: # single status
	    out = self.search_users(id) # id is actually the query string
	return out

if __name__ == "__main__":
    qq = qq()

    # prepare args
    if len(sys.argv) <= 2:
	print qq.usage
	sys.exit()
    else:
	try:
	    id = long(sys.argv[1])
	except ValueError:
	    id = sys.argv[1]
    # primary option
    if len(sys.argv) > 2:
	opt = sys.argv[2]
	if opt == "-ut" or opt == "--user-timeline":
	    opt = 1 # user timeline
	elif opt == "-u" or opt == "--users":
	    opt = 2 # users
	elif opt == "-fr" or opt == "--friends" or opt == "--idol":
	    opt = 3 # friends
	elif opt == "-fl" or opt == "--followers" or opt == "--fans":
	    opt = 4 # followers
	elif opt == "-rp" or opt == "--reposts":
	    opt = 7 # reposts
	elif opt == "-cm" or opt == "--comments":
	    opt = 8 # comments
	elif opt == "-ss" or opt == "--single-status":
	    opt = 9 # single status
	elif opt == "-st" or opt == "--search-t":
	    opt = 10 # search posts
	elif opt == "-su" or opt == "--search-users":
	    opt = 11 # search users
	else:
	    print self.usage # single status
	    sys.exit()
    # secondary options
    for i in range(3,len(sys.argv)):
	if sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
    	    qq.verbose = True
	elif sys.argv[i] == "-c" or sys.argv[i] == "--counts":
    	    output_counts = True
	elif sys.argv[i] == "-a" or sys.argv[i] == "--get-all":
    	    qq.getall = True
	elif sys.argv[i] == "-fs" or sys.argv[i] == "--force-screenname":
    	    qq.force_screenname = True
	    fname = str(sys.argv[1])
	elif sys.argv[i] == "-co" or sys.argv[i] == "--check-only":
	    qq.checkonly = True
	elif sys.argv[i] == "-u" or sys.argv[i] == "--update":
    	    qq.doupdate = True
	elif sys.argv[i] == "-srp" or sys.argv[i] == "--save-range-partition":
	    qq.saveRP = True
	elif sys.argv[i] == "-i" or sys.argv[i] == "--index":
	    qq.index = True
	elif sys.argv[i] == "-dc" or sys.argv[i] == "--double-check":
    	    qq.doublecheck = str(sys.argv[i+1])

    out = qq.dispatch(opt, id)
    out["id"] = id
    out = [out] # put in an array for consistency with list of ids

    if qq.verbose:
	print out
