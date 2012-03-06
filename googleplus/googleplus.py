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
    getall = False
    actors = list()
    toleranceNotToBeginningCount = 0
    toleranceNotToBeginning = 10
    MAX_TRIES_ACTIVITIES = 6
    API_WAIT_SECS = 5

    def __init__(self):
	self.googlepluskey = mypass.getGooglePlusKey()
	self.pgconn = mypass.getConn()
	self.http = httplib2.Http()
	self.api_key = self.googlepluskey["api_key"]

    def people(self, data):
	#if self.verbose:
	#    print data
	r = data
	if "image" in data and data["image"] is not None:
	    r["image_url"] = data["image"]["url"]
	if "name" in data and data["name"] is not None:
	    obj = data["name"]
	    for a in ["familyName", "givenName", "middleName", "honorificPrefix", "honorificSuffix"]:
		if a in obj and obj[a] is not None and len(obj[a]) > 0:
		    try:
			r[a.lower()] = obj[a].encode("utf8")
		    except:
			r[a.lower()] = obj[a]
	for a in ["displayName","url","image_url","objectType","nickname","tagline","birthday","currentLocation","relationshipStatus","hasApp","aboutMe","gender"]:
	    if a in data:
		try:
		    r[a.lower()] = data[a].encode("utf8")
		except:
		    r[a.lower()] = data[a]
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
	print url + "?" + urllib.urlencode(data)
	resp, content = self.http.request(url + "?" + urllib.urlencode(data))
	js = json.loads(content)
	start_time_db = time.time()
	out = self.people(js)
	self.time_db += time.time() - start_time_db
	return out

    def people_search(self, query, language="en", maxResults=20, pageToken=""):
	loops = 0
	if len(pageToken) > 0:
	    time.sleep(self.api_wait_secs)
	    self.recurse_depth += 1
	    print "recurse: %d " % self.recurse_depth
	deleted_count = 0
	out = dict()
	url = "https://www.googleapis.com/plus/v1/people"
	data = dict(key=self.api_key, query=query, language=language, maxResults=maxResults, pageToken=pageToken, prettyPrint=self.prettyPrint)
	while True and loops < self.MAX_TRIES_ACTIVITIES:
	    start_time_db = time.time()
	    start_time_api = time.time()
	    resp, content = self.http.request(url + "?" + urllib.urlencode(data))
	    self.time_api = time.time() - start_time_api
	    #out["resp"] = resp
	    js = json.loads(content)
	    loops += 1
	    if "items" in js:
		break
	    time.sleep(self.API_WAIT_SECS)
	#out["content"] = js
	if "nextPageToken" in js:
	    nextPageToken = js["nextPageToken"]
	else:
	    nextPageToken = ""
	#out["dbresp"] = list()
	if "items" in js:
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

    def activities(self, data):
	r = data
	r_attaches = list()
	attachments = list()
	if "image" in data and data["image"] is not None:
	    r["image_url"] = data["image"]["url"]
	if "provider" in data and data["provider"] is not None:
	    r["provider_title"] = data["provider"]["title"]
	if "actor" in data and data["actor"] is not None:
	    r["actor_id"] = data["actor"]["id"]
	if "access" in data and data["access"] is not None:
	    r["access_kind"] = data["access"]["kind"]
	if "object" in data and data["object"] is not None:
	    obj = data["object"]
	    for a in ["objectType", "originalContent", "content"]:
		if a in obj and obj[a] is not None and len(obj[a]) > 0:
		    try:
			r[a.lower()] = obj[a].encode("utf8")
		    except:
			r[a.lower()] = obj[a]
	    if "replies" in obj and obj["replies"] is not None:
		if "totalItems" in obj["replies"]:
		    r["replies_totalitems"] = obj["replies"]["totalItems"]
	    if "plusoners" in obj and obj["plusoners"] is not None:
		if "totalItems" in obj["plusoners"]:
		    r["plusoners_totalitems"] = obj["plusoners"]["totalItems"]
	    if "resharers" in obj and obj["resharers"] is not None:
		if "totalItems" in obj["resharers"]:
		    r["resharers_totalitems"] = obj["resharers"]["totalItems"]
	    if "attachments" in obj and obj["attachments"] is not None:
		r["attachments_totalitems"] = len(obj["attachments"])
		for attachment in obj["attachments"]:
		    try:
			r_attach = self.attachments(attachment)
		    except:
			continue
		    r_attaches.append(r_attach)
		    attachments.append(attachment)
	for a in ["title", "url", "verb", "annotation", "crosspostSource", "address", "placeId", "placeName"]:
	    if a in data:
		try:
		    r[a.lower()] = data[a].encode("utf8")
		except:
		    r[a.lower()] = data[a]
	if "geocode" in data and data["geocode"] is not None and len(data["geocode"]) > 0:
	    latlng = data["geocode"].split(" ")
	    if len(latlng) == 2:
		lat = latlng[0]
		lng = latlng[1]
		wkt_point = "POINT(" + str(lng) + " " + str(lat) + ")"
		#print wkt_point
		r["geocode"] = "SRID=4326;" + wkt_point
	start_time_db = time.time()
	dbresp = self.toDB("googleplus_activities", r, doupdate=self.doupdate)
	print dbresp
	self.time_db += time.time() - start_time_db
	# Adding entities
	dbresp_entities = list()
	if dbresp["success"] or self.entities:
	    for t in ["actor", "object", "access"]:
		if t in r:
		    if t == "actor":
			actor = r[t]
			actor_id = actor["id"]
			if actor_id not in self.actors:
			    dbresp_entity = self.people(actor)
			    dbresp_entity["entity"] = t
			    self.actors.append(actor_id)
			    dbresp_entities.append(dbresp_entity)
		    elif t == "access":
			for x in r[t]["items"]:
			    if "id" in x:
				self.toDB("googleplus_accesses", x)
				self.toDB("googleplus_activitiesaccesses", {"activities_id": r["id"], "accesses_id": x["id"]})
		    elif t == "object":
			print attachments
			for x in attachments:
			    attachment = None
			    if "url" in x and x["url"] is not None:
				attachment_id = x["url"]
			    elif "id" in x and x["id"] is not None:
				attachment_id = x["id"]
			    else:
				continue
			    self.toDB("googleplus_activitiesattachments", {"activities_id": r["id"], "attachment_url": attachment_id})
		    #for x in r[t]:
	if dbresp["success"]:
	    if dbresp["already_exists"]:
		self.already_exists_count += 1
	    else:
		self.newlyadded += 1
	dbresp["entities"] = dbresp_entities
	dbresp["attachments"] = r_attaches
	return dbresp

    def activities_get(self, activity_id):
	url = "https://www.googleapis.com/plus/v1/activities/%s"
	data = dict(key=self.api_key, prettyPrint=self.prettyPrint)
	url = url % str(activity_id)
	if self.verbose:
    	    print url + "?" + urllib.urlencode(data)
	resp, content = self.http.request(url + "?" + urllib.urlencode(data))
	js = json.loads(content)
	start_time_db = time.time()
	out = self.activities(js)
	self.time_db += time.time() - start_time_db
	return out

    def activities_list(self, user_id, collection="public", maxResults=100, pageToken=""):
	self.toleranceNotToBeginningCount = 0
	loops = 0
	url = "https://www.googleapis.com/plus/v1/people/%(user_id)s/activities/%(collection)s"
	data = dict(key=self.api_key, prettyPrint=self.prettyPrint)
	url = url % { "user_id": str(user_id), "collection": str(collection) }
	self.actors.append(str(user_id)) # no need to add self again
	if self.verbose:
	    print url + "?" + urllib.urlencode(data)
	if len(pageToken) > 0:
	    time.sleep(self.api_wait_secs)
	    self.recurse_depth += 1
	    print "recurse: %d " % self.recurse_depth
	deleted_count = 0
	out = dict()
	data = dict(key=self.api_key, user_id=user_id, collection=collection, maxResults=maxResults, pageToken=pageToken, prettyPrint=self.prettyPrint)
	while True and loops < self.MAX_TRIES_ACTIVITIES:
	    start_time_db = time.time()
    	    start_time_api = time.time()
    	    resp, content = self.http.request(url + "?" + urllib.urlencode(data))
    	    self.time_api = time.time() - start_time_api
    	    js = json.loads(content)
	    loops += 1
	    if "items" in js:
		break
	    time.sleep(self.API_WAIT_SECS)
	if "nextPageToken" in js:
	    nextPageToken = js["nextPageToken"]
	else:
	    nextPageToken = ""
	if "items" in js:
	    for item in js["items"]:
		start_time_db = time.time()
		resp = self.activities(item)
		self.time_db += time.time() - start_time_db
		if resp["already_exists"]:
		    self.toleranceNotToBeginningCount += 1
		if self.toleranceNotToBeginningCount >= self.toleranceNotToBeginning:
		    break
	if self.recurse and self.recurse_depth < self.recurse_maxdepth and len(nextPageToken) > 0 and self.toleranceNotToBeginningCount < self.toleranceNotToBeginning:
	    self.activities_list(user_id=user_id, collection=collection, maxResults=maxResults, pageToken=nextPageToken)
	else:
	    out["newly_added"] = self.newlyadded
	    out["time_api"] = self.time_api
	    out["time_db"] = self.time_db
	    out["time_db_entities"] = self.time_db_entities
	return out

    def activities_search(self, query, language="en", maxResults=20, pageToken=""):
	if len(pageToken) > 0:
	    time.sleep(self.api_wait_secs)
	    self.recurse_depth += 1
	    print "recurse: %d " % self.recurse_depth
	deleted_count = 0
	out = dict()
	url = "https://www.googleapis.com/plus/v1/activities"
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
	    self.activities(item)
	    self.time_db += time.time() - start_time_db
	if self.recurse and self.recurse_depth < self.recurse_maxdepth and len(nextPageToken) > 0:
	    self.activities_search(query=query, language=language, maxResults=maxResults, pageToken=nextPageToken)
	else:
	    out["newly_added"] = self.newlyadded
	    out["time_api"] = self.time_api
	    out["time_db"] = self.time_db
	    out["time_db_entities"] = self.time_db_entities
	return out

    def attachments(self, data):
	r = data
	for a in ["image", "fullImage", "embed"]:
	    if a in data and data[a] is not None:
		if "url" in data[a]:
		    r[a.lower() + "_url"] = data[a]["url"]
		if "type" in data[a]:
		    r[a.lower() + "_type"] = data[a]["type"]
		if "height" in data[a]:
		    r[a.lower() + "_height"] = data[a]["height"]
		if "width" in data[a]:
		    r[a.lower() + "_width"] = data[a]["width"]
	for a in ["objectType", "displayName", "content", "url", "image_url", "fullimage_url"]:
	    if a in r and r[a] is not None:
		try:
		    r[a.lower()] = r[a].encode("utf8")
		except:
		    r[a.lower()] = r[a]
	dbresp = self.toDB("googleplus_attachments", r)
	return dbresp

    def comments(self, data):
	r = data
	if "actor" in data and data["actor"] is not None:
	    r["actor_id"] = data["actor"]["id"]
	if "inReplyTo" in data and data["inReplyTo"] is not None and type(data["inReplyTo"]) is types.ListType and len(data["inReplyTo"]) > 0:
	    inreplyto_ids = list()
	    for inreplyto in data["inReplyTo"]:
		if "id" in inreplyto and inreplyto["id"] is not None:
		    inreplyto_ids.append(str(inreplyto["id"]))
	    r["inreplyto"] = '{%s}' % ",".join(inreplyto_ids)
	if "object" in data and data["object"] is not None:
	    obj = data["object"]
	    for a in ["objectType", "content"]:
		if a in obj and obj[a] is not None and len(obj[a]) > 0:
		    try:
			r[a.lower()] = obj[a].encode("utf8")
		    except:
			r[a.lower()] = obj[a]
	for a in ["verb"]:
	    if a in data:
		try:
		    r[a.lower()] = data[a].encode("utf8")
		except:
		    r[a.lower()] = data[a]
	start_time_db = time.time()
	dbresp = self.toDB("googleplus_comments", r, doupdate=self.doupdate)
	print dbresp
	self.time_db += time.time() - start_time_db
	# Adding entities
	dbresp_entities = list()
	if dbresp["success"] or self.entities:
	    for t in ["actor"]:
		if t in r:
		    if t == "actor":
			actor = r[t]
			actor_id = actor["id"]
			if actor_id not in self.actors:
			    dbresp_entity = self.people(actor)
			    print dbresp_entity
			    dbresp_entity["entity"] = t
			    self.actors.append(actor_id)
			    dbresp_entities.append(dbresp_entity)
	if dbresp["success"]:
	    if dbresp["already_exists"]:
		self.already_exists_count += 1
	    else:
		self.newlyadded += 1
	dbresp["entities"] = dbresp_entities
	return dbresp

    def comments_get(self, comment_id):
	url = "https://www.googleapis.com/plus/v1/comments/%s"
	data = dict(key=self.api_key, prettyPrint=self.prettyPrint)
	url = url % str(comment_id)
	if self.verbose:
    	    print url + "?" + urllib.urlencode(data)
	resp, content = self.http.request(url + "?" + urllib.urlencode(data))
	js = json.loads(content)
	start_time_db = time.time()
	out = self.comments(js)
	self.time_db += time.time() - start_time_db
	return out

    def comments_list(self, activity_id, maxResults=100, pageToken="", sortOrder="descending"):
	self.toleranceNotToBeginningCount = 0
	loops = 0
	url = "https://www.googleapis.com/plus/v1/activities/%s/comments"
	data = dict(key=self.api_key, prettyPrint=self.prettyPrint)
	url = url % str(activity_id)
	if self.verbose:
	    print url + "?" + urllib.urlencode(data)
	if len(pageToken) > 0:
	    time.sleep(self.api_wait_secs)
	    self.recurse_depth += 1
	    print "recurse: %d " % self.recurse_depth
	deleted_count = 0
	out = dict()
	data = dict(key=self.api_key, activity_id=activity_id, maxResults=maxResults, pageToken=pageToken, sortOrder=sortOrder, prettyPrint=self.prettyPrint)
	while True and loops < self.MAX_TRIES_ACTIVITIES:
	    start_time_db = time.time()
    	    start_time_api = time.time()
    	    resp, content = self.http.request(url + "?" + urllib.urlencode(data))
    	    self.time_api = time.time() - start_time_api
    	    js = json.loads(content)
	    loops += 1
	    if "items" in js:
		break
	    time.sleep(self.API_WAIT_SECS)
	if "nextPageToken" in js:
	    nextPageToken = js["nextPageToken"]
	else:
	    nextPageToken = ""
	if "items" in js:
	    for item in js["items"]:
		start_time_db = time.time()
		resp = self.comments(item)
		self.time_db += time.time() - start_time_db
		if resp["already_exists"]:
		    self.toleranceNotToBeginningCount += 1
		if self.toleranceNotToBeginningCount >= self.toleranceNotToBeginning:
		    break
	if self.recurse and self.recurse_depth < self.recurse_maxdepth and len(nextPageToken) > 0 and self.toleranceNotToBeginningCount < self.toleranceNotToBeginning:
	    self.comments_list(activity_id=activity_id, maxResults=maxResults, pageToken=nextPageToken, sortOrder=sortOrder)
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
		resp["reason"] = self.pgconn.error
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
    out = dict()

    if len(sys.argv) > 0:
	opt = sys.argv[1]
	if opt == "-p":
	    opt = 2 # people
	if opt == "-a":
	    opt = 3 # activities
	if opt == "-al":
	    opt = 4 # activities list
	if opt == "-c":
	    opt = 5 # comments
	if opt == "-cl":
	    opt = 6 # comments list

    for i in range(2, len(sys.argv)):
	if sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
    	    gp.verbose = True
	if sys.argv[i] == "-r" or sys.argv[i] == "--recursive":
	    gp.recurse = True
	if sys.argv[i] == "-e" or sys.argv[i] == "--entities":
	    gp.entities = True
	if sys.argv[i] == "-u" or sys.argv[i] == "--update":
	    gp.doupdate = True
	if sys.argv[i] == "-a" or sys.argv[i] == "--get-all":
	    gp.getall = True

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
    elif opt == 3:
	try:
	    activity_id = int(sys.argv[2])
	    out = gp.activities_get(activity_id)
	except ValueError:
	    q = ""
	    for i in range(2, len(sys.argv)):
		if not sys.argv[i].startswith("-"):
		    if len(q) > 0:
			q += " "
		    q += sys.argv[i]
	    out = gp.activities_search(q)
    elif opt == 4:
	try:
	    user_id = int(sys.argv[2])
	    out = gp.activities_list(user_id, "public")
	except ValueError:
	    pass
    elif opt == 5:
	try:
	    comment_id = sys.argv[2]
	    out = gp.comments_get(comment_id)
	except ValueError:
	    pass
    elif opt == 6:
	try:
	    activity_id = sys.argv[2]
	    out = gp.comments_list(activity_id)
	except ValueError:
	    pass

    if gp.verbose:
	print out
