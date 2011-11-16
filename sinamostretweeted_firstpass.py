#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import pg
import mypass
import simplejson
import time
import datetime
import string
import types

import sinaweibooauth

# sinamostretweeted.py outputs json of the most retweeted for a given time period

pgconn = mypass.getConn()

usage = "sinamostretweeted_firstpass.py [date start] [optional: date end] [-o filename]"

# default values
fformat = "json"
provid = 81
listid = 0
outfile = ""
nouser = False
counting = False
maxfollowers_default = 100000
maxfollowers = 0
limit = 2000

# Date for minimal created_at 
date_user_created_at_minimal = datetime.datetime.now() - datetime.timedelta(weeks=26)

if len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
    dateend = sys.argv[2]
else:
    dateend = ""
if len(sys.argv) > 1:
    datestart = sys.argv[1]
else:
    print usage
    sys.exit()

if len(datestart) > 0:
    try:
    	datestart = datetime.datetime.strptime(datestart, "%Y-%m-%d %H:%M")
    except ValueError:
	try:
	    datestart = datetime.datetime.strptime(datestart, "%Y-%m-%d")
	except ValueError:
	    print usage
	    sys.exit()

dateend_sql = ""
if len(dateend) > 0:
    try:
    	dateend = datetime.datetime.strptime(dateend, "%Y-%m-%d %H:%M")
    except ValueError:
	try:
	    dateend = datetime.datetime.strptime(dateend, "%Y-%m-%d")
	except ValueError:
	    print usage
	    sys.exit()
    dateend_sql = "AND s.created_at <= '%s'" % datetime.datetime.strftime(dateend, '%Y-%m-%d')

for i in range(2,len(sys.argv)):
    if sys.argv[i] == "-rt" or sys.argv[i] == "--retweets":
	justretweets = True
    if sys.argv[i] == "-o" or sys.argv[i] == "--output-filename":
	if i + 1 < len(sys.argv):
	    outfile = sys.argv[i+1]
    if sys.argv[i] == "-c" or sys.argv[i] == "--csv":
	fformat = "csv"
	import csv
    if sys.argv[i] == "-C" or sys.argv[i] == "--count":
	counting = True
    if sys.argv[i] == "-p" or sys.argv[i] == "--provid":
	if i + 1 < len(sys.argv):
	    try:
		provid = int(sys.argv[i+1])
	    except:
		continue
    if sys.argv[i] == "-maxfol" or sys.argv[i] == "--max-followers":
	if i + 1 < len(sys.argv):
	    try:
		maxfollowers = int(sys.argv[i+1])
	    except:
		maxfollowers = maxfollowers_default
		continue
	else:
	    maxfollowers = maxfollowers_default
    if sys.argv[i] == "-no" or sys.argv[i] == "--no-userinfo":
	nouser = True
    if sys.argv[i] == "-l" or sys.argv[i] == "--listid":
	if i + 1 < len(sys.argv):
	    try:
		listid = int(sys.argv[i+1])
	    except:
		continue


if maxfollowers > 0:
    maxfollowers_sql = "AND ru.followers_count < " + str(maxfollowers)
else:
    maxfollowers_sql = ""

sw = sinaweibooauth.SinaWeiboOauth()

'''
isostart = datestart.isocalendar()
isoend = dateend.isocalendar()
yearisostart = isostart[0]
weekisostart = isostart[1]
yearisoend = isoend[0]
weekisoend = isoend[1]

sw_tables_arr = list()
for x in range(yearisostart,yearisoend+1):
    if yearisostart == yearisoend:
	weekisorange = range(weekisostart, weekisoend+1)
    elif yearisostart == x:
	weekisorange = range(weekisostart, 54)
    elif yearisoend == x:
	weekisorange = range(1, weekisoend)
    for y in weekisorange:
	sw_tables_arr.append("SELECT * FROM rp_sinaweibo_y%(year)dw%(week)d y%(year)dw%(week)d" % { "year": x, "week": y })
sw_tables_rs_arr = ["SELECT * FROM rp_sinaweibo_y%(year)dw%(week)d y%(year)dw%(week)d" % { "year": yearisostart_weekbefore, "week": weekisostart_weekbefore }]
sw_tables_rs_arr.extend(sw_tables_arr)
sw_tables = " UNION ".join(sw_tables_arr)
sw_tables_rs = " UNION ".join(sw_tables_rs_arr)
'''
if len(dateend) <= 0:
    dateend = datetime.datetime.now()
sw_tables = sw.getRangePartitionSQL(datestart, dateend)
sw_tables_rs = sw.getRangePartitionSQL(datestart - datetime.timedelta(weeks=1), dateend)
sw_tables = "(%s)" % sw_tables
#sw_tables_rs = "(%s)" % sw_tables_rs
sw_tables_rs = "rp_sinaweibo"

#sw_tables = sw_tables_rs = "rp_sinaweibo"

sql = "SELECT s.retweeted_status, COUNT(s.retweeted_status) AS retweeted_count, \
ARRAY_AGG(s.user_id) user_ids, ARRAY_AGG(s.created_at) creation_dates, ARRAY_AGG(u.gender) genders, ARRAY_AGG(u.followers_count) followers_counts, \
MAX(rs.id) AS id, MAX(rs.created_at) AS created_at, MIN(u.created_at) AS min_user_created_at, COUNT(DISTINCT u.id) AS distinct_users \
FROM %(sw_tables)s s LEFT JOIN sinaweibo_users u on s.user_id = u.id \
LEFT JOIN %(sw_tables_rs)s rs ON s.retweeted_status = rs.id \
LEFT JOIN sinaweibo_users AS ru ON rs.user_id = ru.id " % { "sw_tables_rs": sw_tables_rs, "sw_tables": sw_tables }

if listid <= 0:
    sql_where = "WHERE u.province = %(provid)d %(maxfollowers)s \
AND s.created_at >= '%(date)s' %(dateend)s \
AND s.retweeted_status IS NOT NULL \
GROUP BY s.retweeted_status "\
% { 'provid': provid, 'date': datetime.datetime.strftime(datestart, '%Y-%m-%d') + " " + datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), \
'dateend': dateend_sql, 'maxfollowers': maxfollowers_sql }
else:
    sql_where = "LEFT JOIN sinaweibo_userlist ul ON u.id = ul.user_id \
WHERE ul.list_id = %(listid)d AND s.created_at >= '%(date)s' %(dateend)s \
AND s.retweeted_status IS NOT NULL \
GROUP BY s.retweeted_status "\
% { 'listid': listid, 'date': datetime.datetime.strftime(datestart, '%Y-%m-%d') + " " + datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), \
'dateend': dateend_sql, 'maxfollowers': maxfollowers_sql }

sql += sql_where
sql += "LIMIT %d " % (limit * 50)

sql = "SELECT retweeted_status, retweeted_count, user_ids, creation_dates, genders, followers_counts, id, created_at \
FROM (%(sql_inner)s) foo WHERE min_user_created_at <= '%(date_user_created_at_minimal)s' ORDER BY distinct_users DESC LIMIT %(limit)d " \
% { "sql_inner": sql, "date_user_created_at_minimal": datetime.datetime.strftime(date_user_created_at_minimal, '%Y-%m-%d'), "limit": limit }

if counting:
    print "Not counting rows..."
    pass
    print "Counting rows..."
    sql_total = "SELECT NOW(), COUNT(*) FROM sinaweibo s WHERE created_at >= '%(date)s' %(dateend)s " \
 % { 'date': datetime.datetime.strftime(datestart, '%Y-%m-%d') + " " + datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), 'dateend': dateend_sql }
    try:
	res_count = pgconn.query(sql_total).getresult()
	count = res_count[0][0]
    except pg.ProgrammingError, pg.InternalError:
	print "A SQL error occured: "
	print sql_total
	sys.exit()
    except:
	print "Error: "
	print res_count
	sys.exit()

    print "Rows count:" + count

print "Format: " + fformat
print "Trying SQL..."
print sql

try:
    res = pgconn.query(sql)
except pg.ProgrammingError, pg.InternalError:
    print "A SQL error occured: "
    print sql
    sys.exit()

# Added 2011-08-22
# For RP
# Go through retweets, check min-max file and mark potentially interesting tables and IDs
# SQL query in those partitions to get the IDs we can find
# Go through rows again, and put the tweets we could find
# Prepare the minmax file for Python
print "Checking minmax"
cr = csv.DictReader(open("/var/data/sinaweibo/rp/rp-minmaxids-sw.csv", "r"))
minmaxids = dict()
for csvrow in cr:
    if not csvrow["year"] in minmaxids: # put year
	minmaxids[csvrow["year"]] = dict()
    if not csvrow["week"] in minmaxids[csvrow["year"]]: # put week
	minmaxids[csvrow["year"]][csvrow["week"]] = dict()
    if len(csvrow["min"]) > 0 and len(csvrow["max"]) > 0:
	minmaxids[csvrow["year"]][csvrow["week"]]["min"] = long(csvrow["min"])
	minmaxids[csvrow["year"]][csvrow["week"]]["max"] = long(csvrow["max"])
years_sorted = sorted(minmaxids.keys())
yearsweeks_sorted = dict()
for yeariso in years_sorted: # get a dict per year of sorted weeks
    yearsweeks_sorted[yeariso] = sorted(minmaxids[yeariso].keys())
#print yearsweeks_sorted
# Mark range partitions to check and keep IDs of weibos
print "Marking range partitions"
rp_tocheck = list()
ids_tocheck = list()
if fformat == "csv": #CSV
    rows = res.dictresult()
    myrows = list()
    #rows = [{"retweeted_status": 11582880157}, {"retweeted_status": 11775213904}, {"retweeted_status": 14120974047}, {"retweeted_status": 13075642891}, {"retweeted_status": 12223179606}]
    for r in rows:
	myrows.append(r)
	thisid = r["retweeted_status"]
	thismin = None
	thismax = None
	if "id" not in r or r["id"] is None: # when a RTs may not be found in the partition we have checked
	    donethisid = False
	    last_within_minmax = False
	    # we go in the min-max
	    for year in years_sorted:
		if donethisid:
		    break
		for week in yearsweeks_sorted[year]:
		    minmax = minmaxids[year][week] # the minmax we are checking currently
		    lastmin = thismin # not used
		    lastmax = thismax # not used
		    if "min" not in minmax or "max" not in minmax: # don't check empty partitions
			continue
		    thismin = minmax["min"]
		    thismax = minmax["max"]
		    if thismin is None or thismax is None: # don't check empty partitions
			continue
		    if thisid >= thismin and thisid <= thismax: # within this partition
			yw_str = str(year) + "," + str(week)
			if yw_str not in rp_tocheck:
			    rp_tocheck.append(yw_str)
			if last_within_minmax:
	    		    donethisid = True
		       	    break
			else:
			    last_within_minmax = True
			    continue
	    if last_within_minmax:
		ids_tocheck.append(str(thisid))
	    #print thisid
	    #print donethisid
	    #print last_within_minmax
    #print rp_tocheck
    #print ids_tocheck
# Get the weibos that can be found in the DB
if len(rp_tocheck) > 0 and len(ids_tocheck) > 0:
    sw_tables_arr = list()
    for x in rp_tocheck:
	yw = x.split(",")
	year = int(yw[0])
	week = int(yw[1])
	sw_tables_arr.append("SELECT id, created_at FROM rp_sinaweibo_y%(year)dw%(week)d y%(year)dw%(week)d" % { "year": year, "week": week })
    sw_tables = " UNION ".join(sw_tables_arr)
    sql_weibos = "SELECT * FROM (%(sw_tables)s) s WHERE id IN (%(ids)s) " % { "sw_tables": sw_tables, "ids": ",".join(ids_tocheck) }
    print sql_weibos
    res_weibos = pgconn.query(sql_weibos).dictresult()
    #print res_weibos
    for rw in res_weibos:
	for mr in myrows:
	    if mr["id"] is None and rw["id"] == mr["retweeted_status"]:
		mr = dict(mr.items() + rw.items())

#sql_weibos = "SELECT * FROM rp_sinaweibo WHERE id IN (%(ids)s) " % { "sw_tables": sw_tables, "ids": ",".join(ids_tocheck) }

#dt = datetime.datetime.now()
#dtstr = datetime.datetime.strftime(dt,'%Y%m%d-%H%M')
#fname = outfile + "_" + dtstr + "." + fformat
fname = outfile + "." + fformat
f = open(fname, "w")

if fformat == "csv": #CSV
    #rows = res.getresult()
    cw = csv.DictWriter(f, ["retweeted_status", "retweeted_count", "user_ids", "creation_dates", "genders", "followers_counts", "id", "created_at"], delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar="\\", lineterminator="\n")
    for r in myrows:
	cw.writerow(r)
	if "created_at" in r and r["created_at"] is not None:
	    if len(r["created_at"]) > 0:
		sw.saveRangePartitionByIdDate(r["id"], datetime.datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S"))
else:
    rows = res.dictresult()
    l = list()
    for r in rows:
	l.append(r)
    f.write(simplejson.dumps(l))


