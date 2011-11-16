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
import string

import mypass
import sinaweibooauth

__author__ = "Cedric Sam"

usage = "sinatrace.py [id of status to trace] "
table_name = "rp_sinaweibo"
pgconn = mypass.getConn()

def sinatrace(tid, minimal=False, extra_fields=False, get_users=False, outformat="json"):
    # For RP: Should try to find the created_at if it's not known or given as argument...
    sw = sinaweibooauth.SinaWeiboOauth()
    sw.setToken(sw.sinaweiboOauth["oauth_token"], sw.sinaweiboOauth["oauth_token_secret"]) 
    try:
	tid = long(tid)
    except ValueError:
	print usage
	sys.exit()
    if extra_fields:
	extra_fields = ", u.name user_name, u.screen_name user_screen_name, u.domain user_domain, \
u.province user_province, u.city user_city, u.gender user_gender, \
u.followers_count user_followers_count, u.friends_count user_friends_count, u.retrieved user_retrieved "
    else:
	extra_fields = ""
    '''
    rps = sw.getRangePartitionByIds([tid])
    for rp in rps:
	x = rp.split(",")
	year = int(x[0])
	week = int(x[1])
	break
    isocal = datetime.datetime.now().isocalendar()
    year_now = isocal[0]
    week_now = isocal[1]
    sw_tables_arr = list()
    for x in range(year,year_now+1):
	if year == year_now:
	    myrange = range(week,week_now+1)
	elif x == year:
	    myrange = range(week,54)
	elif x == year_now:
	    myrange = range(1,week)
	for y in myrange:
	    sw_tables_arr.append("SELECT * FROM rp_sinaweibo_y%(year)dw%(week)d" % { "year": x, "week": y })
    sw_tables = " UNION ".join(sw_tables_arr)
    '''
    sql = "SELECT s.id, s.created_at, s.user_id, s.screen_name, s.text, u.id AS user_id_ref %(extra_fields)s \
FROM rp_sinaweibo s LEFT JOIN sinaweibo_users u ON s.user_id = u.id \
WHERE retweeted_status = %(tid)d ORDER BY s.id " % {"tid": tid, "extra_fields": extra_fields }#, "sw_tables": sw_tables}
    #print sql
    rows = pgconn.query(sql).dictresult()
    out = dict()
    rts = list()
    count = 0
    out["generated_start"] = datetime.datetime.now().strftime("%c")
    ids_cache = dict()
    missing_users = list()
    missing_users_ids = list()
    for r in rows:
	if r["screen_name"] not in ids_cache:
	    ids_cache[r["screen_name"]] = r["user_id"]
	m = re.findall(u"//@([^\:：。\.\：/@\-，,【\[ ]*)", r["text"])
	#m = re.findall(u"//@([^：/@:, ]*)", r["text"])
	refs = list()
	for refname in m:
	    refname = refname.split("：")[0]
	    ref = dict()
	    if refname in ids_cache:
		ref["id"] = ids_cache[refname]
	    else:
		#sql_ref = "SELECT u.id FROM sinaweibo_users u WHERE u.screen_name = '%(ref)s' " % { 'ref': refname }
		sql_ref = "SELECT s.user_id as id FROM sinaweibo s WHERE s.retweeted_status = %(tid)d AND s.created_at < '%(created_at)s' AND s.screen_name = '%(ref)s' ORDER BY s.created_at DESC LIMIT 1 " % { 'tid': tid, "created_at": r["created_at"], 'ref': refname.replace("'","''")}
		#print sql_ref
		try:
		    rows_ref = pgconn.query(sql_ref).dictresult()
		except pg.ProgrammingError as e:
		    print e
		    print refname
		    continue
		if len(rows_ref) == 0: # get from users table
		    sql_ref_fromusers = "SELECT u.id FROM sinaweibo_users u WHERE u.screen_name = '%(ref)s' " % { 'ref': refname }
		    rows_ref = pgconn.query(sql_ref_fromusers).dictresult()
		if len(rows_ref) > 0:
		    ref["id"] = rows_ref[0]["id"]
		    ids_cache[refname] = ref["id"]
		else:
		    if get_users:
			resp = sw.user(None, refname)
    			try:
    			    ref["id"] = resp["data"][0]["id"]
			    ids_cache[refname] = ref["id"]
    			except KeyError:
			    ref["id"] = None
	    		    ids_cache[refname] = None
			    missing_users.append(refname)
		    else:
			ref["id"] = None
		    	ids_cache[refname] = None
			missing_users.append(refname)
	    ref["name"] = refname
	    refs.append(ref)
	    count += 1
	r["references"] = refs
	if get_users and r["user_id_ref"] is None: # users who reposted, but not in our DB yet
	    missing_users_ids.append(r["user_id"])
	rts.append(r)
    out["missing_users"] = missing_users
    out["missing_users_count"] = len(missing_users)
    out["reposts"] = rts
    out["reposts_count"] = len(rts)
    out["generated"] = long(time.mktime(datetime.datetime.now().timetuple())) * 1000
    out["generated_end"] = datetime.datetime.now().strftime("%c")
    if get_users and len(missing_users_ids) > 0:
	f = open(str(tid) + "_missing_users_ids.txt", "w")
	for x in missing_users_ids:
	    f.write(str(x) + "\n")
    if get_users and len(missing_users) > 0: # print missing users list
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

def gviz_trends(tid, req_id=0, interval="", period="", province=0, listid=0, outformat="json"):
    try:
	tid = long(tid)
    except ValueError:
	sys.exit()
    import gviz_api
    sql_interval = "to_char(date_trunc('hour', s.created_at), 'YYYY-MM-DD HH24:MI')"
    # Interval part
    dateformat = "%Y-%m-%d %H:%M"
    if interval == "":
	delta_t = datetime.timedelta(hours=1)
    elif string.lower(interval) == "10m":
	delta_t = datetime.timedelta(minutes=10)
	sql_interval = "substring(to_char(s.created_at, 'YYYY-MM-DD HH24:MI') for 15)||0"
    elif string.lower(interval[len(interval)-1]) == "m":
	mins_interval = interval[0:len(interval)-1]
	delta_t = datetime.timedelta(minutes=mins_interval)
	sql_interval = "to_char(date_trunc('hour', s.created_at) + \
INTERVAL '%(mins_interval)s min' * ROUND(date_part('minute', s.created_at) \
/ %(mins_interval)s.0), 'YYYY-MM-DD HH24:MI')" % {"mins_interval": mins_interval}
    elif string.lower(interval) == "d":
	dateformat = "%Y-%m-%d"
	delta_t = datetime.timedelta(days=1)
	sql_interval = "date(s.created_at) "
    else:
	delta_t = datetime.timedelta(hours=1)
    # Period part
    if len(period) > 0:
	measure = string.lower(period[len(period)-1])
	try:
	    nb = int(str(period[0:len(period)-1]))
	except ValueError:
	    nb = 1
	today = datetime.date.today()
	datedatatype = "string"
	if measure == "d":
	    basetime = today - datetime.timedelta(days=nb)
	elif measure == "w":
	    basetime = today - datetime.timedelta(weeks=nb)
	elif measure == "m":
	    basetime = datetime.date(today.year+(today.month-nb-1)/12,(today.month-nb-1)%12+1, today.day)
    else:
	basetime = None
    if basetime is None:
	sql_period = ""
	sw_tables = "sinaweibo"
    else:
	basetime = datetime.datetime.combine(basetime, datetime.time())
	sql_period = " AND s.created_at >= '%s' " % basetime.strftime("%Y-%m-%d")
	import sinaweibooauth
	sw = sinaweibooauth.SinaWeiboOauth()
	sw_tables = "(%s)" % sw.getRangePartitionSQL(basetime)
    sql_location = ""
    sql_listidjoin = ""
    sql_listid = ""
    if int(listid) > 0:
	sql_listidjoin = "LEFT JOIN sinaweibo_userlist ul ON u.id = ul.user_id "
	sql_listid = " AND ul.list_id = %d " % int(listid)
    if int(province) > 0:
	sql_location = " AND u.province = %d " % int(province)
    sql = "SELECT %(interval)s AS time, COUNT(*) AS count, COUNT(DISTINCT s.user_id) AS users \
FROM %(sw_tables)s s LEFT JOIN sinaweibo_users u ON s.user_id = u.id %(sql_listidjoin)s WHERE retweeted_status = %(tid)d %(sql_period)s %(sql_location)s %(sql_listid)s GROUP BY time ORDER BY time " \
% {"tid": tid, "interval": sql_interval, "sql_period": sql_period, "sql_location": sql_location, "sql_listidjoin": sql_listidjoin, "sql_listid": sql_listid, "sw_tables": sw_tables }
    rows = pgconn.query(sql).dictresult()
    description = {"time": ("string", "Time"),
		    "count": ("number", "statuses"),
		    "users": ("number", "distinct users")}
    columns_order = "time", "count", "users"
    order_by = "time"
    data = []
    if basetime is None:
	basetime = datetime.datetime.strptime(rows[0]["time"], dateformat)
    elif len(rows) > 0:
	try:
	    datastart = datetime.datetime.strptime(rows[0]["time"], dateformat)
	except:
	    dateformat = "%Y-%m-%d"
	    datastart = datetime.datetime.strptime(rows[0]["time"], dateformat)
	while basetime + delta_t < datastart:
	    data.append({"time": datetime.datetime.strftime(basetime, dateformat), "count": 0, "users": 0})
	    basetime += delta_t
    for r in rows:
	thistime = datetime.datetime.strptime(r["time"], dateformat)
	while basetime + delta_t < thistime:
	    #data.append({"time": basetime, "count": 0, "users": 0})
	    data.append({"time": datetime.datetime.strftime(basetime, dateformat), "count": 0, "users": 0})
	    basetime += delta_t
	#data.append({"time": thistime, "count": r["count"], "users": r["users"]})
	data.append({"time": r["time"], "count": r["count"], "users": r["users"]})
	basetime = thistime + delta_t
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    if outformat == "json":
	return data_table.ToJSon(columns_order, order_by, req_id)
    elif outformat == "jsonresp":
	return data_table.ToJSonResponse(columns_order, order_by, req_id)
    else:
	return data_table.ToJSCode("jscode_data", columns_order, order_by, req_id)

if __name__ == "__main__":
    if len(sys.argv) < 2:
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
