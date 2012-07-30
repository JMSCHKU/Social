#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sinaurl.py resolves sinaurl.cn urls and saves the link to a database

import sys
import pg
import os
import time
import datetime
import string
import types
import pycurl
import json
import re

import mypass
import sinaurl

PATH = "/var/data/sinaweibo/sinaurl/archive/"
DEFAULT_LIMIT = 200
DEFAULT_HRS = 24

usage = "sinaurl.archiver.py [last n hours / def: %d] [limit nb] " % DEFAULT_HRS

pgconn = mypass.getConn()

checkdeleted = False

if len(sys.argv) < 1:
    hrs = DEFAULT_HRS
    limit = DEFAULT_LIMIT
else:
    try:
	hrs = int(sys.argv[1])
    except ValueError:
	hrs = DEFAULT_HRS
    except IndexError:
	hrs = DEFAULT_HRS
    if len(sys.argv) > 1:
	try:
	    limit = int(sys.argv[2])
	except:
	    limit = DEFAULT_LIMIT
    else:
	limit = DEFAULT_LIMIT
    if len(sys.argv) >= 1:
	for i in range(1,len(sys.argv)):
	    if sys.argv[i] == "-d":
		limit = int(DEFAULT_LIMIT / 8)
		checkdeleted = True

nowdate = datetime.datetime.now()
lastdate = nowdate - datetime.timedelta(hours=hrs)

spamsites = list()
try:
    fspamsites = open("/var/data/sinaweibo/spam/spamsites.txt", "r")
    for x in fspamsites:
	try:
	    x = x.strip()
	except:
	    continue
	spamsites.append(x)
    fspamsites.close()
except:
    pass

spamposts = list()
try:
    fspamposts = open("/var/data/sinaweibo/spam/spamposts.txt", "r")
    for x in fspamposts:
	try:
	    x = str(int(x.strip()))
	except:
	    continue
	spamposts.append(x)
    fspamposts.close()
except:
    pass

def checkSpam(location):
    for spamsite in spamsites:
	try:
	    m = re.match("http://[^/]*%s" % spamsite, location)
	except:
	    continue
	if type(m) is not types.NoneType:
	    return True
    return False

def fetchFile(hashurl, locationurl, path):
    f = open(path + "/" + hashurl + '_' + nowdate.strftime('%Y%m%d-%H%M') + '.html', 'w')
    try:
	c = pycurl.Curl()
	c.setopt(pycurl.URL, locationurl)
	c.setopt(pycurl.FOLLOWLOCATION, 0)
	c.setopt(pycurl.WRITEFUNCTION, f.write)
	c.perform()
	c.close()
	f.close()
    except Exception:
	pass
    f.close()


if len(spamposts) > 0:
    spamposts_sql = "WHERE rt_status_id NOT IN (%s)" % ",".join(spamposts)
else:
    spamposts_sql = ""

if checkdeleted is False:
    sql = "SELECT foo.sinaurl[1] sinaurl_full, foo.sinaurl[2] sinaurl_base, foo.sinaurl[3] sinaurl_hash, su.*, distinct_posts, distinct_users, rt_status_id FROM \
    (SELECT COUNT(distinct s1.id) distinct_posts, COUNT(distinct s1.user_id) distinct_users, \
    regexp_matches(s2.text, '(http:\/\/(sinaurl\.cn|t\.cn)\/([\\\\w]+))') sinaurl, \
    MIN(s1.retweeted_status) rt_status_id \
    FROM rp_sinaweibo s1 \
    LEFT JOIN rp_sinaweibo s2 ON s1.retweeted_status = s2.id \
    LEFT JOIN sinaweibo_userlist ul ON s1.user_id = ul.user_id \
    WHERE s1.created_at >= '%(lastdate)s' AND ul.list_id = 1 \
    GROUP BY sinaurl ORDER BY distinct_users DESC LIMIT %(limit)d) foo \
    LEFT JOIN sinaweibo_sinaurl su ON foo.sinaurl[2] = su.hash AND foo.sinaurl[1] = su.base \
    %(spamposts_sql)s " \
    % {"lastdate": lastdate.strftime('%Y-%m-%d %H:%M'), "limit": limit, "spamposts_sql": spamposts_sql }

    print sql
    #sys.exit()

    start_time_db = time.time()
    res = pgconn.query(sql).dictresult()
    time_db = time.time() - start_time_db
    print time_db

try:
    archivepath1 = PATH + "sinaurl.cn/" + nowdate.strftime('%Y%m%d-%H%M')
    archivepath2 = PATH + "t.cn/" + nowdate.strftime('%Y%m%d-%H%M')
    print archivepath1
    os.mkdir(archivepath1, 0755)
    print archivepath2
    os.mkdir(archivepath2, 0755)
except OSError:
    pass
    #print "OSError"
    #sys.exit()

newspamposts = list()

if checkdeleted is False:
    for x in res:
	print x
	archivepath = PATH + x["sinaurl_base"] + "/" + nowdate.strftime('%Y%m%d-%H%M')
	if x["sinaurl_base"] == "sinaurl.cn":
	    archivepath = archivepath1
	elif x["sinaurl_base"] == "t.cn": 
	    archivepath = archivepath2
	if x["hash"] is None:
	    try:
		sinaurl.sinaurl(x["sinaurl_full"]) # resolves the URL and puts in the DB
	    except:
		continue
	    res_sinaurl = pgconn.get("sinaweibo_sinaurl", {"hash": x["sinaurl_hash"], "base": x["sinaurl_base"]})
	    #print res_sinaurl
	    #print res_sinaurl[0]["hash"] + "\t" + res_sinaurl[0]["location"]
	    myhash = res_sinaurl["hash"]
	    mybase = res_sinaurl["base"]
	    mylocation = res_sinaurl["location"]
	else:
	    #print x["hash"] + "\t" + x["location"]
	    myhash = x["hash"]
	    mybase = x["base"]
	    mylocation = x["location"]
	is_spam = checkSpam(mylocation)
	print "is_spam: %s" % is_spam
	if is_spam and str(x["rt_status_id"]) not in spamposts:
	    newspamposts.append(str(x["rt_status_id"]))
	if myhash is None or mylocation is None:
	    print "Error: hash and location are None"
	    continue
	fetchFile(myhash, mylocation, archivepath)
elif checkdeleted is True:
    fdel = open("/var/www/social/sinaweibo/lastpermissiondenied.json", "r")
    js = json.loads(fdel.read())
    if "hits" in js:
	statuses = js["hits"]
    else:
	statuses = js
    ids_visited = list()
    for x in statuses:
	print x["status_id"]
	if x["status_id"] in ids_visited or len(ids_visited) > limit:
	    continue
	if "http://" in x["text"] or ("rt_text" in x and x["rt_text"] is not None and "http://" in x["rt_text"]):
	    urls = list()
	    if "http://" in x["text"]:
		m = re.search(r"http:\/\/([A-z0-9\.]+)\/([\w]+)", x["text"])
		if m is not None:
		    sinaurl_base = m.group(1)
		    sinaurl_hash = m.group(2)
		    ids_visited.append(x["status_id"])
		    if sinaurl_base == "sinaurl.cn":
			archivepath = archivepath1
		    elif sinaurl_base == "t.cn": 
			archivepath = archivepath2
		    else:
			archivepath = None
		    try:
			#print "http://" + sinaurl_base + "/" + sinaurl_hash
			sinaurl.sinaurl("http://" + sinaurl_base + "/" + sinaurl_hash)
			res_sinaurl = pgconn.get("sinaweibo_sinaurl", {"hash": sinaurl_hash, "base": sinaurl_base})
			print res_sinaurl["location"]
			#print res_sinaurl
			#print res_sinaurl[0]["hash"] + "\t" + res_sinaurl[0]["location"]
			#myhash = res_sinaurl["hash"]
			#mybase = res_sinaurl["base"]
			mylocation = res_sinaurl["location"]
			is_spam = checkSpam(mylocation)
			print "is_spam: %s" % is_spam
			fetchFile(sinaurl_hash, mylocation, archivepath)
		    except:
			continue
		else:
		    continue
	    if "rt_text" in x and x["rt_text"] is not None and "http://" in x["rt_text"] and x["retweeted_status"] is not None:
		m = re.search(r"http:\/\/([A-z0-9\.]+)\/([\w]+)", x["rt_text"])
		if m is not None:
		    sinaurl_base = m.group(1)
		    sinaurl_hash = m.group(2)
		    ids_visited.append(x["retweeted_status"])
		    if sinaurl_base == "sinaurl.cn":
			archivepath = archivepath1
		    elif sinaurl_base == "t.cn": 
			archivepath = archivepath2
		    else:
			continue
		    try:
			#print "http://" + sinaurl_base + "/" + sinaurl_hash
			sinaurl.sinaurl("http://" + sinaurl_base + "/" + sinaurl_hash)
			res_sinaurl = pgconn.get("sinaweibo_sinaurl", {"hash": sinaurl_hash, "base": sinaurl_base})
			print res_sinaurl["location"]
			mylocation = res_sinaurl["location"]
			is_spam = checkSpam(mylocation)
			print "is_spam: %s" % is_spam
			fetchFile(sinaurl_hash, mylocation, archivepath)
		    except:
			continue
		else:
		    continue


if len(newspamposts) > 0:
    print newspamposts
    try:
	fnewspamposts = open("/var/data/sinaweibo/spam/spamposts.txt", "a")
	#first = True
	for x in newspamposts:
	    fnewspamposts.write("\n")
	    fnewspamposts.write(x)
	fnewspamposts.close()
    except:
	pass
