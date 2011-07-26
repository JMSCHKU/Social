#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import mypass
import socket
import httplib
import json
import time
import datetime
import types
import csv

import mypass
import twitter
import string

class TwitterDB():

    psql_dateformat = '%Y-%m-%d %H:%M:%S %Z'
    twitter_dateformat = '%a %b %d %H:%M:%S %z %Y'
    
    usage = "twitter.db.py [OPT:id] [primary opts] [sec opts]"
    verbose = False
    fieldnames_users = ["description", "location", "url", "profile_image_url", "created_at", "name", "time_zone", "followers_count", "friends_count", "statuses_count", "listed_count", "verified"]

    def __init__(self):
	twitterOAuth = mypass.getTwitterOauth()
	api = twitter.Api(consumer_key=twitterOAuth["consumer_key"],
    	    consumer_secret=twitterOAuth["consumer_secret"],
	    access_token_key=twitterOAuth["oauth_token"],
    	    access_token_secret=twitterOAuth["oauth_token_secret"],
	    cache=None)
	self._api = api
	self._pgconn = mypass.getConn()
	socket.setdefaulttimeout(150)

    def getTopHashtags(self, start_date, end_date=None, list_id=None, limit=200):
	end_date_sql = "AND t.created_at < '%s' "
	try:
	    if list_id is None or list_id <= 0:
		list_id_sql = ""
	    else:
		list_id_sql = "AND ul.list_id = %d" % list_id
	except TypeError as e:
	    try:
		list_id = string.split(list_id,",")
	    except AttributeError:
		pass
	    list_id_copy = list()
	    for x in list_id:
		list_id_copy.append(str(x))
    	    list_id_sql = "AND (ul.list_id = %s)" % string.join(list_id_copy, " OR ul.list_id = ")
	if end_date is None:
	    end_date_sql = end_date_sql % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	else:
	    try:
		end_date_sql = end_date_sql % end_date.strftime("%Y-%m-%d %H:%M:%S")
	    except:
		end_date_sql = end_date_sql % end_date
	try:
	    start_date_sql = "t.created_at >= '%s'" % start_date.strftime("%Y-%m-%d %H:%M:%S")
	except:
	    start_date_sql = "t.created_at >= '%s'" % start_date
	sql = "SELECT regexp_matches(text, E'#([^\\\\s\\\\[\\\\]]+)', 'g') hashtag \
FROM (SELECT text FROM tweets t \
WHERE %(start_date)s %(end_date)s \
%(list_id)s GROUP BY retweeted_status ORDER BY \
retweeted_statuses_count DESC LIMIT %(limit)d) foo LEFT JOIN tweets t \
ON foo.rts = t.id WHERE foo.rts IS NOT NULL \
ORDER BY retweeted_statuses_count DESC, CAST(REPLACE(retweet_count, '+', '') AS INTEGER) DESC " \
	% { "start_date": start_date_sql, "end_date": end_date_sql, "list_id": list_id_sql, "limit": limit }
	return sql

    def getMostRetweeted(self, start_date, end_date=None, list_id=None, limit=200, get_users=True):
	end_date_sql = "AND t.created_at < '%s' "
	try:
	    if list_id is None or list_id <= 0:
		list_id_sql = ""
	    else:
		list_id_sql = "AND ul.list_id = %d" % list_id
	except TypeError as e:
	    try:
		list_id = string.split(list_id,",")
	    except AttributeError:
		pass
	    list_id_copy = list()
	    for x in list_id:
		list_id_copy.append(str(x))
    	    list_id_sql = "AND (ul.list_id = %s)" % string.join(list_id_copy, " OR ul.list_id = ")
	if end_date is None:
	    end_date_sql = end_date_sql % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	else:
	    try:
		end_date_sql = end_date_sql % end_date.strftime("%Y-%m-%d %H:%M:%S")
	    except:
		end_date_sql = end_date_sql % end_date
	try:
	    start_date_sql = "t.created_at >= '%s'" % start_date.strftime("%Y-%m-%d %H:%M:%S")
	except:
	    start_date_sql = "t.created_at >= '%s'" % start_date
	sql = "SELECT *, ST_AsKML(geo) FROM \
(SELECT retweeted_status rts, count(distinct t.id) \
retweeted_statuses_count FROM twitter_userlist ul LEFT JOIN tweets t ON \
ul.user_id = t.user_id WHERE %(start_date)s %(end_date)s \
%(list_id)s GROUP BY retweeted_status ORDER BY \
retweeted_statuses_count DESC LIMIT %(limit)d) foo LEFT JOIN tweets t \
ON foo.rts = t.id WHERE foo.rts IS NOT NULL \
ORDER BY retweeted_statuses_count DESC, CAST(REPLACE(retweet_count, '+', '') AS INTEGER) DESC " \
	% { "start_date": start_date_sql, "end_date": end_date_sql, "list_id": list_id_sql, "limit": limit }
	if self.verbose:
	    print sql
	res = self._pgconn.query(sql).dictresult()
	out = dict()
	rts = list()
	uids = list()
	uids_str = list()
	for x in res:
	    if x["id"] is None or x["user_id"] is None or x["screen_name"] is None:
		if x["user_id"] is None or x["screen_name"] is None:
		    status = self.getSingleTweet(x["rts"], doupdate=True)
		else:
		    status = self.getSingleTweet(x["rts"])
		if type(status) is types.StringType:
		    if status.find("suspended") >= 0:
			try:
			    sql_user = "UPDATE twitter_users SET suspended = NOW() WHERE id = %d " % x["user_id"]
			    row = self._pgconn.query(sql_user)
			except pg.ProgrammingError, pg.InternalError:
			    print pg
		    continue
		elif status is not None:
		    try:
			x.update(status)
		    except:
			try:
			    x.update(status.AsDict())
			except:
			    continue
			x["user_id"] = x["user"]["id"]
			x["screen_name"] = x["user"]["screen_name"]
		    del x["favorited"]
		    del x["truncated"]
		    del x["user"]
		    del x["retweeted"]
		    del x["source"]
	    try:
		x["created_at"] = long(time.mktime(datetime.datetime.strptime(x["created_at"] + ' GMT', self.psql_dateformat).timetuple())) * 1000
	    except:
		try:
		    x["created_at"] = long(time.mktime(datetime.datetime.strptime(x["created_at"], self.twitter_dateformat).timetuple())) * 1000
		except:
		    pass
	    x["id_str"] = str(x["id"])
	    x["retweeted_status_str"] = str(x["rts"])
	    if x["user_id"] is not None:
		uids.append(x["user_id"])
	    #uids_str.append(str(x["user_id"]))
	    rts.append(x)
	uids = set(uids)
	for uid in uids:
	    uids_str.append(str(uid))
	out["rts"] = rts
	if get_users:
	    sql_users = "SELECT id FROM twitter_users WHERE id IN (%(ids)s) ORDER BY id " % { "ids": ",".join(uids_str) }
	    res_users = self._pgconn.query(sql_users).getresult()
	    uids_missing = uids
	    for x in res_users:
		uids_missing.remove(x[0])
	    for x in uids_missing:
		print x
		r = self.getSingleUser(x, doupdate=True)
	    sql_users = "SELECT * FROM twitter_users WHERE id IN (%(ids)s) ORDER BY id " % { "fields": ",".join(self.fieldnames_users), "ids": ",".join(uids_str) }
	    res_users = self._pgconn.query(sql_users).dictresult()
	    print len(res_users)
	    out["users"] = res_users
	return out

    def getSingleTweet(self, id, doupdate=False):
	try:
	    id = long(id)
	except ValueError as e:
	    print e
	    return None
	except TypeError as e:
	    print e
	    return None
	try:
	    status = self._api.GetStatus(id)
	except twitter.TwitterError as e:
	    print id
	    print e
	    return e
	#if status["retweeted_status"] is not None:
    	#    status["retweeted_status"] = status["retweeted_status"]["id"]

	#r = self.status_to_row(status)
	r = status.AsDict()
	if self.verbose:
	    print r

	r["text"] = r["text"].encode("utf8")
	if "id" in r["user"]:
	    r["user_id"] = r["user"]["id"]
	if "retweeted_status" in r:
	    r["retweeted_status"] = r["retweeted_status"]["id"]
	if "screen_name" in r["user"]:
	    r["screen_name"] = r["user"]["screen_name"]
	if "source" in r and r["source"] is not None:
	    r["source"] = r["source"].encode("utf8")
	if "geo" in r and r["geo"] is not None:
	    if "type" in r["geo"] and r["geo"]["type"] == "Point" and "coordinates" in r["geo"] and r["geo"]["coordinates"] is not None and len(r["geo"]["coordinates"]) == 2:
		lat = r["geo"]["coordinates"][0]
		lng = r["geo"]["coordinates"][1]
		wkt_point = "POINT(" + str(lng) + " " + str(lat) + ")"
		r["geo"] = "SRID=4326;" + wkt_point
	#r["created_at"] = long(time.mktime(datetime.datetime.strptime(r["created_at"] + ' GMT', self.psql_dateformat).timetuple())) * 1000
	row = None
	try:
	    if self.verbose:
		print "Trying insert..."
	    row = self._pgconn.insert("tweets", r)
	except pg.ProgrammingError, pg.InternalError:
	    if self.verbose:
		print self._pgconn.error
	    if doupdate:
		if self.verbose:
		    print "Trying update..."
		try:
		    row = self._pgconn.update("tweets", r)
		except pg.ProgrammingError, pg.InternalError:
		    if self.verbose:
			print self._pgconn.error
	    pass
	if row is not None:
	    return row
	else:
	    return status

    def getSingleUser(self, id, doupdate=True):
	try:
	    id = long(id)
	except ValueError as e:
	    print e
	    return None
	except TypeError as e:
	    print e
	    return None
	try:
	    user = self._api.GetUser(id)
	except twitter.TwitterError as e:
	    print id
	    if e.message().find("suspended") >= 0:
		sql_user = "UPDATE twitter_users SET suspended = NOW() WHERE id = %d " % id
		row = self._pgconn.query(sql_user)
	    print e
	    return None
	row = self.saveSingleUser(user.AsDict(), doupdate)
	return row

    def saveSingleUser(self, u, doupdate=False):
	u["retrieved"] = "NOW()"
	for a in ["name", "description", "location", "url"]:
	    if a in u and u[a] is not None:
		u[a] = u[a].encode("utf8")
	try:
	    if self.verbose:
		print "Trying insert on user..."
	    row = self._pgconn.insert("twitter_users", u)
	except pg.ProgrammingError, pg.InternalError:
	    if self.verbose:
		print self._pgconn.error
	    if doupdate:
		if self.verbose:
		    print "Trying update on user..."
		try:
		    row = self._pgconn.update("twitter_users", u)
		except pg.ProgrammingError, pg.InternalError:
		    if self.verbose:
			print self._pgconn.error
	    pass
	if self.verbose:
	    print row
	return row

if __name__ == "__main__":
    tw = TwitterDB()
    start_daysago = 3
    outformat = "print"
    opt = 0
    list_id = None
    suffix = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    doupdate = False

    # prepare args
    if len(sys.argv) <= 1:
	print tw.usage
	sys.exit()

    # primary option
    if sys.argv[1].startswith("-"):
	opt = sys.argv[1]
    else:
	id = long(sys.argv[1])
	if len(sys.argv) > 2:
	    opt = sys.argv[2]
	else:
	    opt = 1
    if opt == "-mrt" or opt == "--most-retweeted":
	opt = 2 # most retweeted
    elif opt == "-ht" or opt == "--top-hashtags":
	opt = 3 # top hashtags
    if type(opt) is not types.IntType:
	opt = 1

    # secondary options
    for i in range(2,len(sys.argv)):
	if sys.argv[i] == "-hk" or sys.argv[i] == "--hong-kong":
	    list_id = [3,4,5]
	if sys.argv[i] == "-zh" or sys.argv[i] == "--china":
	    list_id = 1
	if sys.argv[i] == "-v" or sys.argv[i] == "--verbose":
    	    tw.verbose = True
	if sys.argv[i] == "-u" or sys.argv[i] == "--update":
    	    doupdate = True
	if sys.argv[i] == "-j" or sys.argv[i] == "--json":
    	    outformat = "json"
	if sys.argv[i] == "--csv" or sys.argv[i] == "-csv":
    	    outformat = "csv"
	if sys.argv[i] == "-d":
	    if len(sys.argv) > i+1:
		try:
		    start_daysago = int(sys.argv[i+1])
		except ValueError:
		    pass
	if sys.argv[i].startswith("--days="):
	    start_daysago = sys.argv[i].split("=",1)[1]
	if sys.argv[i] == "-s":
	    if len(sys.argv) > i+1:
		suffix = sys.argv[i+1]

    suffix = str(start_daysago) + "d-" + suffix

    tw.fieldnames_users.remove("created_at")
    tw.fieldnames_users.append("u_created_at")
    if opt == 1:
	status = tw.getSingleTweet(id, doupdate=doupdate)
	fieldnames = status.AsDict().keys().extend(tw.fieldnames_users)
	if type(status) is types.StringType:
	    print status
	elif outformat == "json":
	    print json.dumps(status.AsDict())
	elif outformat == "csv":
	    #cw = csv.writer(open("singletweet-%(id)s-%(date)s.csv" % { "id": id, "date": datetime.datetime.now().strftime("%Y%m%d-%H%M") }, "w"),quoting=csv.QUOTE_MINIMAL)
	    cw = csv.DictWriter(open("singletweet-%(id)s-%(date)s.csv" % { "id": id, "date": datetime.datetime.now().strftime("%Y%m%d-%H%M") }, "w"),quoting=csv.QUOTE_MINIMAL)
	    cw.writerow(fieldnames)
	    cw.writerow(status.AsDict())
	else:
	    print status.AsDict()
    elif opt == 2:
	mostRts = tw.getMostRetweeted(datetime.datetime.utcnow() - datetime.timedelta(start_daysago), list_id=list_id)
	dtstr_end = long(time.mktime(datetime.datetime.now().timetuple())) * 1000
	fieldnames = mostRts["rts"][0].keys()
	fieldnames.extend(tw.fieldnames_users)
	fieldnames_header = dict()
	fieldnames_empty = dict()
	for x in fieldnames:
	    fieldnames_header[x] = x
	    fieldnames_empty[x] = None
	if outformat == "json":
	    fname = "mostretweeted-%s.json" % suffix
	    f = open(fname, "w")
	    f.write(json.dumps({"rts":mostRts["rts"], "dategen":dtstr_end, "users": mostRts["users"]}))
	    f.close()
	    print fname
	elif outformat == "csv":
	    #cw = csv.writer(open("mostretweeted-%s.csv" % datetime.datetime.now().strftime("%Y%m%d-%H%M"), "w"),quoting=csv.QUOTE_MINIMAL)
	    cw = csv.DictWriter(open("mostretweeted-%s.csv" % suffix, "w"),fieldnames,quoting=csv.QUOTE_MINIMAL)
	    cw.writerow(fieldnames_header)
	    for x in mostRts["rts"]:
		if tw.verbose:
		    print x
    		    print type(x)
		for u in mostRts["users"]:
		    if u["id"] == x["user_id"]:
			u["u_created_at"] = u["created_at"]
			del u["created_at"]
			x.update(u)
			break
		cw.writerow(x)
	else:
	    print mostRts
    elif opt == 3:
	topHashtags = tw.getTopHashtags(datetime.datetime.utcnow() - datetime.timedelta(start_daysago), list_id=list_id)
	print topHashtags
    #print mostRts
    #simplejson.dumps(mostRts)
    #tw.getSingleTweet(sys.argv[1])

