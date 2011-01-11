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

# sinamostretweeted.py outputs json of the most retweeted for a given time period

pgconn = mypass.getConn()

usage = "sinamostretweeted.py [date start] [optional: date end] [-o filename]"

# default values
fformat = "json"
provid = 81
outfile = ""
nouser = False
counting = False

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
    if sys.argv[i] == "-no" or sys.argv[i] == "--no-userinfo":
	nouser = True


sql = "SELECT s.retweeted_status, COUNT(s.retweeted_status) AS retweeted_count, \
ARRAY_AGG(s.user_id), ARRAY_AGG(s.created_at), ARRAY_AGG(u.gender), ARRAY_AGG(u.followers_count), \
MAX(rs.id) AS id \
FROM sinaweibo_users AS u RIGHT JOIN sinaweibo s on u.id = s.user_id \
LEFT JOIN sinaweibo as rs ON s.retweeted_status = rs.id \
WHERE u.province = %(provid)d AND s.created_at >= '%(date)s' %(dateend)s \
AND s.retweeted_status IS NOT NULL \
GROUP BY s.retweeted_status ORDER BY retweeted_count DESC "\
% { 'provid': provid, 'date': datetime.datetime.strftime(datestart, '%Y-%m-%d'), 'dateend': dateend_sql }

if counting:
    print "Counting rows..."
    sql_total = "SELECT NOW(), COUNT(*) FROM sinaweibo s WHERE created_at >= '%(date)s' %(dateend)s " \
 % { 'date': datetime.datetime.strftime(datestart, '%Y-%m-%d'), 'dateend': dateend_sql }
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

#dt = datetime.datetime.now()
#dtstr = datetime.datetime.strftime(dt,'%Y%m%d-%H%M')
#fname = outfile + "_" + dtstr + "." + fformat
fname = outfile + "." + fformat
f = open(fname, "w")

if fformat == "csv": #CSV
    rows = res.getresult()
    cw = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar="\\", lineterminator="\n")
    for r in rows:
	cw.writerow(r)
else:
    rows = res.dictresult()
    l = list()
    for r in rows:
	l.append(r)
    f.write(simplejson.dumps(l))


