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

class GooglePlus():

    api_wait_secs = 2
    googlepluskey = None
    pgconn = None
    http = None
    api_key = None
    verbose = False
    prettyPrint = "false"
    recurse = False
    recurse_depth = 0
    recurse_maxdepth = 50
    time_api = 0
    time_db = 0
    time_db_u = 0
    time_db_entities = 0
    newlyadded = 0
    already_exists_count = 0
    entities = False
    doupdate = False

    def __init__(self):
	self.googlepluskey = mypass.getGooglePlusKey()
	self.pgconn = mypass.getConn()
	self.http = httplib2.Http()
	self.api_key = self.googlepluskey["api_key"]

    def people(self, data):
	#if self.verbose:
	#    print data
	r = data
	r["image_url"] = data["image"]["url"]
	r["displayname"] = data["displayName"]
	for a in ["displayName","url","image_url","objectType","nickname","tagline","birthday","currentLocation","relationshipStatus","hasApp","aboutMe","gender"]:
	    if a in data:
		try:
		    r[a.lower()] = data[a].encode("utf8")
		except:
		    r[a.lower()] = data[a]
	#r["id"] = int(data["id"])
	start_time_db = time.time()
	dbresp = self.toDB("googleplus_people", r, doupdate=self.doupdate)
	self.time_db += time.time() - start_time_db
	# Adding entities
	dbresp_entities = list()
	if dbresp["success"] or self.entities:
	    for t in ["urls", "emails", "placesLived", "organizations"]:
		if t in r:
		    for x in r[t]:
			entity = dict()
			entity["parent_id"] = r["id"]
			entity["parent_type"] = "people"
			for a in ["value","type","name","department","title","startdate","enddate","location","description"]:
			    if a in x:
				try:
				    entity[a.lower()] = x[a].encode("utf8")
				except:
				    entity[a.lower()] = x[a]
			if "primary" in x and x["primary"]:
			    entity["is_primary"] = True
			start_time_db_entities = time.time()
			dbresp_entity = self.toDB("googleplus_%s" % t.lower(), entity)
			dbresp_entity["entity"] = t
			self.time_db_entities += time.time() - start_time_db_entities
			dbresp_entities.append(dbresp_entity)
	    dbresp["entities"] = dbresp_entities
	if dbresp["success"]:
	    if dbresp["already_exists"]:
		self.already_exists_count += 1
	    else:
		self.newlyadded += 1
	return dbresp

    def people_get(self, user_id):
	url = "https://www.googleapis.com/plus/v1/people/%s"
	data = dict(key=self.api_key, prettyPrint=self.prettyPrint)
	url = url % str(user_id)
	resp, content = self.http.request(url + "?" + urllib.urlencode(data))
	js = json.loads(content)
	start_time_db = time.time()
	out = self.people(js)
	self.time_db += time.time() - start_time_db
	return out

    def people_search(self, query, language="en", maxResults=20, pageToken=""):
	if len(pageToken) > 0:
	    time.sleep(self.api_wait_secs)
	    self.recurse_depth += 1
	    print "recurse: %d " % self.recurse_depth
	deleted_count = 0
	out = dict()
	url = "https://www.googleapis.com/plus/v1/people"
	data = dict(key=self.api_key, query=query, language=language, maxResults=maxResults, pageToken=pageToken, prettyPrint=self.prettyPrint)
	start_time_db = time.time()
	start_time_api = time.time()
	resp, content = self.http.request(url + "?" + urllib.urlencode(data))
	self.time_api = time.time() - start_time_api
	#out["resp"] = resp
	js = json.loads(content)
	#out["content"] = js
	if "nextPageToken" in js:
	    nextPageToken = js["nextPageToken"]
	else:
	    nextPageToken = ""
	#out["dbresp"] = list()
	for item in js["items"]:
	    start_time_db = time.time()
	    self.people(item)
	    self.time_db += time.time() - start_time_db
	if self.recurse and self.recurse_depth < self.recurse_maxdepth and len(nextPageToken) > 0:
	    self.people_search(query=query, language=language, maxResults=maxResults, pageToken=nextPageToken)
	else:
	    out["newly_added"] = self.newlyadded
	    out["time_api"] = self.time_api
	    out["time_db"] = self.time_db
	    out["time_db_entities"] = self.time_db_entities
	return out

    def toDB(self, tablename, data, doupdate=False, updatefirst=False):
	if self.pgconn is None:
	    self.pgconn = mypass.getConn()
	resp = { "success": False, "already_exists": False }
	#r = self.pgconn.insert(tablename, data)
	#r = self.pgconn.update(tablename, data)
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
		if r is not None and "id" in r:
		    resp["id"] = r["id"]
	    except pg.ProgrammingError, pg.InternalError:
		if self.pgconn.error.find('duplicate key value violates unique constraint') > 0:
		    resp["already_exists"] = True
		    try:
			if doupdate:
			    r = self.pgconn.update(tablename, data)
			    resp["success"] = True
			    if r is not None and "id" in r:
				resp["id"] = r["id"]
		    except:
			resp["reason"] = self.pgconn.error
			pass

	#pgconn.close()
	return resp

if __name__ == "__main__":
    gp = GooglePlus()

    if len(sys.argv) > 0:
	opt = sys.argv[1]
	if opt == "-p":
	    opt = 2 # people

    for i in range(2, len(sys.argv)):
	if sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
    	    gp.verbose = True
	if sys.argv[i] == "-r" or sys.argv[i] == "--recursive":
	    gp.recurse = True
	if sys.argv[i] == "-e" or sys.argv[i] == "--entities":
	    gp.entities = True
	if sys.argv[i] == "-u" or sys.argv[i] == "--update":
	    gp.doupdate = True

    if opt == 2:
	try:
	    user_id = int(sys.argv[2])
	    out = gp.people_get(user_id)
	except ValueError:
	    q = ""
	    for i in range(2, len(sys.argv)):
		if not sys.argv[i].startswith("-"):
		    if len(q) > 0:
			q += " "
		    q += sys.argv[i]
	    out = gp.people_search(q)

    if gp.verbose:
	print out
