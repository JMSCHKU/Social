#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sinatrace.py traces the reposts of a status specified from ID

import sys
import pg
import re
try: import simplejson as json
except ImportError: import json
import time
import datetime
import mypass

usage = "sinatrace.py [id of status to trace] "
table_name = "sinaweibo"
pgconn = mypass.getConn()

def sinatrace(tid, minimal=False, extra_fields=False, get_users=False, outformat="json"):
    try:
	tid = long(tid)
    except ValueError:
	print usage
	sys.exit()
    if extra_fields:
	extra_fields = ", u.name user_name, u.screen_name user_screen_name, u.domain user_domain, \
u.province user_province, u.city user_city, \
u.followers_count user_followers_count, u.friends_count user_friends_count, u.retrieved user_retrieved "
    else:
	extra_fields = ""
    sql = "SELECT s.id, s.created_at, s.user_id, s.text %(extra_fields)s \
FROM sinaweibo s LEFT JOIN sinaweibo_users u ON s.user_id = u.id \
WHERE retweeted_status = %(tid)d ORDER BY s.id " % {"tid": tid, "extra_fields": extra_fields}
    rows = pgconn.query(sql).dictresult()
    out = dict()
    rts = list()
    count = 0
    out["generated_start"] = datetime.datetime.now().strftime("%c")
    ids_cache = dict()
    missing_users = list()
    for r in rows:
	m = re.findall("//@([^: ]*)", r["text"])
	refs = list()
	for refname in m:
	    ref = dict()
	    if refname in ids_cache:
		ref["id"] = ids_cache[refname]
	    else:
		sql_ref = "SELECT u.id FROM sinaweibo_users u WHERE u.screen_name = '%(ref)s' " % { 'ref': refname }
		rows_ref = pgconn.query(sql_ref).dictresult()
		if len(rows_ref) > 0:
		    ref["id"] = rows_ref[0]["id"]
		    ids_cache[refname] = ref["id"]
		else:
		    ref["id"] = None
		    ids_cache[refname] = None
		    missing_users.append(refname)
	    ref["name"] = refname
	    refs.append(ref)
	    count += 1
	r["references"] = refs
	rts.append(r)
    out["missing_users"] = missing_users
    out["missing_users_count"] = len(missing_users)
    out["reposts"] = rts
    out["generated"] = long(time.mktime(datetime.datetime.now().timetuple())) * 1000
    out["generated_end"] = datetime.datetime.now().strftime("%c")
    if get_users and len(missing_users) > 10: # print missing users list
	f = open(str(tid) + "_missing_users.txt", "w")
	for x in missing_users:
	    f.write(str(x) + "\n")
    if outformat == "json":
	if minimal:
	    return json.dumps(out)
	else:
	    return json.dumps(out, sort_keys=True, indent=4)
    else:
	return out

if __name__ == "__main__":
    if len(sys.argv) < 1:
	print usage
	sys.exit()
    minimal = False
    extra_fields = False
    get_users = False
    for i in range(2,len(sys.argv)):
	if sys.argv[i] == "-min" or sys.argv[i] == "--minimal":
	    minimal = True
	if sys.argv[i] == "-e" or sys.argv[i] == "--extra-fields":
	    extra_fields = True
	if sys.argv[i] == "-u" or sys.argv[i] == "--users":
	    get_users = True
    print sinatrace(sys.argv[1], minimal, extra_fields, get_users)
