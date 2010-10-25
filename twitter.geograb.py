#!/usr/bin/env python

# twitter.geograb.py is a script that outputs in CSV all tweets from the
# Twitter Search API that are geocoded or have a location field
# according to an area specified in the head of the code or as cmdline args

import sys
import httplib
import json
import time
import datetime
import string

TWITTER_SEARCH = "/search.json"
#HKU
#lat = "22.28255921"
#lng = "114.13975775"
#rad = "1km"
#HK
lat = "22.33"
lng = "114.12"
rad = "30km"
tocsv = True
page = "1"

for i in range(len(sys.argv)):
    if sys.argv[i].startswith("--lat="):
	lat = sys.argv[i].split("=")[1]
    if sys.argv[i].startswith("--lng="):
	lng = sys.argv[i].split("=")[1]
    if sys.argv[i].startswith("--rad="):
	rad = sys.argv[i].split("=")[1]
    if sys.argv[i] == "-co" or sys.argv[i] == "--csv-out":
	tocsv = True
    if sys.argv[i].startswith("--page="):
	page = sys.argv[i].split("=")[1]

url = TWITTER_SEARCH + "?q=&show_user=true&rpp=100&result_type=recent&geocode=" + lat + "," + lng + "," + rad
url += "&page=" + page
#print url
conn = httplib.HTTPConnection("search.twitter.com")
ok = False
try:
    conn.request("GET", url)
except (Exception):
    sys.exit(sys.exc_info())
r = conn.getresponse()
data = r.read()
if r.status == 200:
    ok = True
    js = json.loads(data)
if ok:
    #print "id,from_user_id,from_user,lat,lng,iso_language_code,created_at,text"
    for x in js["results"]:
	if x["geo"] is not None or x["location"].startswith(lat[0:2]):
	    r = list()
	    if tocsv:
		r.append(str(x["id"]))
		r.append(str(x["from_user_id"]))
		r.append(x["from_user"])
		if x["geo"] is not None:
		    r.append(str(x["geo"]["coordinates"][0])) #lat
		    r.append(str(x["geo"]["coordinates"][1])) #lng
		elif x["location"].startswith(lat[0:2]):
		    try:
			r.append(x["location"].split(",")[0])
			r.append(x["location"].split(",")[1])
		    except:
			r.extend(["",""])
		else:
		    r.extend(["",""])
		if "iso_language_code" in x:
		    r.append(x["iso_language_code"])
		else:
		    r.append("")
		r.append(datetime.datetime.strptime(x["created_at"], "%a, %d %b %Y %H:%M:%S +0000").strftime('%Y-%m-%d %H:%M:%S'))
		r.append('"' + string.replace(x["text"],'"','""') + '"')
		first = True
		out = ""
		try:
		    for y in r:
			if not first:
			    out += "," + y
			else:
			    out += y
			first = False
		except UnicodeDecodeError:
		    if not first:
			out += "," + y.encode("utf8")
		    else:
			out += y.encode("utf8")
		    first = False
		print out.encode("utf8")
