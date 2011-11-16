#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import pg
import mypass
import json
import time
import datetime
import string
import types
import csv
import sinaweibooauth

# sinamostretweeted.py outputs json of the most retweeted for a given time period

pgconn = mypass.getConn()

usage = "sinamostretweeted_secondpass.py [input file with ids (can be CSV)] [output file name]"

if len(sys.argv) > 2:
    infile = sys.argv[1]
    outfile = sys.argv[1]
else:
    print usage
    sys.exit()

fformat = "json"
nouser = False
outfile = ""
for i in range(2,len(sys.argv)):
    if sys.argv[i] == "-c" or sys.argv[i] == "--csv":
	fformat = "csv"
    if sys.argv[i] == "-no" or sys.argv[i] == "--no-userinfo":
	nouser = True
    if sys.argv[i] == "-o" or sys.argv[i] == "--output-filename":
	if i + 1 < len(sys.argv):
	    outfile = sys.argv[i+1]

retweeted_user_ids = list()
retweeted_counts = dict()
retweeted_users = dict()
retweeted_times = dict()
retweeted_user_gender = dict()
retweeted_male = dict()
retweeted_female = dict()
distinct_retweeted_users = dict()
distinct_retweeted_users_gender = dict()
print infile
fi = open(infile, 'r')
csv.field_size_limit(524288)
cr = csv.reader(fi, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
'''
for line in fi:
    retweeted_user_ids.append(line.split(",")[0])
    retweeted_counts[line.split(",")[0]] = int(line.split(",")[1])
'''
for row in cr:
    retweeted_user_ids.append(row[0])
    retweeted_counts[row[0]] = int(row[1])
    retweeted_users[row[0]] = json.loads(row[2].replace("{","[").replace("}","]"))
    retweeted_times[row[0]] = json.loads(row[3].replace("{","[").replace("}","]"))
    genders = row[4].replace("{","").replace("}","").split(",")
    retweeted_male[row[0]] = genders.count("m")
    retweeted_female[row[0]] = genders.count("f")
    i = 0
    # keep a record of distinct users and their gender
    distinct_retweeted_users[row[0]] = list()
    distinct_retweeted_users_gender[row[0]] = list()
    for x in retweeted_users[row[0]]:
	if not x in distinct_retweeted_users[row[0]]:
	    distinct_retweeted_users[row[0]].append(x)
	    distinct_retweeted_users_gender[row[0]].append(genders[i])
	i += 1

if len(retweeted_user_ids) <= 0:
    print "Infile was empty: " + infile
    sys.exit()

sw = sinaweibooauth.SinaWeiboOauth()
print retweeted_user_ids
rps = sw.getRangePartitionByIds(ids=retweeted_user_ids)
print rps
# Prepare union-ised tables
'''
sw_tables = "rp_sinaweibo"
if len(rps) > 0 and len(retweeted_user_ids) > 0:
    sw_tables_arr = list()
    for x in rps:
	yw = x.split(",")
	year = int(yw[0])
	week = int(yw[1])
	sw_tables_arr.append("SELECT id, user_id, created_at, thumbnail_pic, bmiddle_pic, original_pic, text FROM rp_sinaweibo_y%(year)dw%(week)d y%(year)dw%(week)d" % { "year": year, "week": week })
    sw_tables = " UNION ".join(sw_tables_arr)
    sw_tables = "(%s)" % sw_tables
'''
sw_tables = "rp_sinaweibo"

if nouser:
    sql_statuses = "SELECT s.id, s.user_id, u.id as user_user_id \
FROM %(sw_tables)s s LEFT JOIN sinaweibo_users AS u ON s.user_id = u.id \
WHERE s.id IN (%(ids)s) " % { 'sw_tables': sw_tables, 'ids': ",".join(retweeted_user_ids) }
else:
    sql_statuses = "SELECT s.id, s.user_id, u.name as user_name, \
u.followers_count, u.friends_count, u.statuses_count, u.profile_image_url, \
u.created_at as user_created_at, u.province, u.city, u.verified, \
s.created_at, s.thumbnail_pic, s.bmiddle_pic, s.original_pic, s.text, \
s.reposts_count, s.comments_count, s.mlevel, \
p.provname, c.cityname, c.name_en as cityname_en, \
array_to_string((regexp_split_to_array(p.name_en, E', '))[array_length(regexp_split_to_array(p.name_en, E', '),1)-1:array_length(regexp_split_to_array(p.name_en, E', '),1)],',') as provname_en \
FROM %(sw_tables)s s \
LEFT JOIN sinaweibo_users AS u ON s.user_id = u.id \
LEFT JOIN sinaweibo_provinces AS p ON u.province = p.provid AND p.cityid = 1 \
LEFT JOIN sinaweibo_provinces AS c ON u.province = c.provid AND u.city = c.cityid \
WHERE s.id IN (%(ids)s) " % { 'sw_tables': sw_tables, 'ids': ",".join(retweeted_user_ids) }

dt = datetime.datetime.now()
#dtstr = datetime.datetime.strftime(dt,'%Y%m%d%H%M')
#dtstr_start = datetime.datetime.strftime(dt,'%Y-%m-%d %H:%M')
#fname = outfile + "_" + dtstr + "." + fformat
fname = outfile + "." + fformat

psql_dateformat = '%Y-%m-%d %H:%M:%S %Z'
print fname
f = open(fname, "w")
print sql_statuses
if fformat == "csv": #CSV
    res_statuses = pgconn.query(sql_statuses).getresult()
    cw = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar="\\", lineterminator="\n")
    r = list()
    for rs in res_statuses:
	l = []
	#l.extend(rs[0:1])
	#l.append(retweeted_counts[str(rs[0])])
	#l.extend(rs[2:len(rs)-1])
	l.extend(rs[0:len(rs)])
	r.append(l)
    #print r
    r_sorted = sorted(r, key=lambda k: k[1], reverse=True)
    for rs in r_sorted:
	try:
	    cw.writerow(rs)
	except Exception as e:
	    print e
	    continue
else: # default: JSON
    res_statuses = pgconn.query(sql_statuses).dictresult()
    r = list()
    for rs in res_statuses:
	l = {}
	rs["count"] = retweeted_counts[str(rs["id"])]
	rs["users"] = retweeted_users[str(rs["id"])]
	rs["times"] = retweeted_times[str(rs["id"])]
	rs["created_at"] = long(time.mktime(datetime.datetime.strptime(rs["created_at"] + ' HKT', psql_dateformat).timetuple())) * 1000
	if rs["user_created_at"] is not None:
	    rs["user_created_at"] = long(time.mktime(datetime.datetime.strptime(rs["user_created_at"] + ' HKT', psql_dateformat).timetuple())) * 1000
	rs["male_count"] = retweeted_male[str(rs["id"])]
	rs["female_count"] = retweeted_female[str(rs["id"])]
	rs["distinct_users"] = distinct_retweeted_users[str(rs["id"])]
	rs["distinct_users_count"] = len(rs["distinct_users"])
	rs["distinct_male_count"] = distinct_retweeted_users_gender[str(rs["id"])].count("m")
	rs["distinct_female_count"] = distinct_retweeted_users_gender[str(rs["id"])].count("f")
	#l = {"id":rs["id"],"user_id":rs["user_id"],"user_name":rs["user_name"],"count":retweeted_counts[str(rs["id"])]}
	#rs["count"] = retweeted_counts[str(rs[0])]
	r.append(rs)
    r_sorted = sorted(r, key=lambda k: k["count"], reverse=True)
    #dtstr_end = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M')
    dtstr_end = long(time.mktime(datetime.datetime.now().timetuple())) * 1000
    f.write(json.dumps({"rts":r_sorted, "dategen":dtstr_end}))
f.close()


