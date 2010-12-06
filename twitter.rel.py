# -*- coding: utf-8 -*-

import sys
import pg
import httplib
import simplejson

pgconn = pg.DB('YOUR_DB', '127.0.0.1', 5432, None, None, 'YOUR_USERNAME', 'YOUR_PASSWORD')

usage = "twitter.rel [user_id] [--followers|--following] [OPT:--no-duplicates]"

no_duplicates = False
followers = False
following = False
if len(sys.argv) > 1:
    user_id = sys.argv[1]
    if len(sys.argv) > 2:
	for i in range(2,len(sys.argv)):
	    if sys.argv[i] == "-nd" or sys.argv[i] == "--no-duplicates":
		no_duplicates = True
	    elif sys.argv[i] == "--followers" or sys.argv[i] == "-2":
		followers = True
	    elif sys.argv[i] == "--friends" or sys.argv[i] == "-1" or sys.argv[i] == "--following":
		following = True
else:
    print usage
    sys.exit()

if not followers and not following:
    print "must specify at least --following or --followers"
    print usage
    sys.exit()
elif followers:
    t = "twitter_followers"
    pre = "followers"
elif following:
    t = "twitter_friends"
    pre = "friends"

try:
    user_id = str(int(user_id))
except (ValueError):
    print "argument invalid: given " + user_id
    print usage
    sys.exit()

if no_duplicates:
    res = pgconn.query("SELECT COUNT(*) FROM " + t + " WHERE source_id = " + str(user_id)).getresult()
    #print res[0][0]
    if res[0][0] > 0:
	print str(res[0][0]) + " " + pre + " already for user [" + user_id + "]: this script will exit..."
	sys.exit()

if user_id > 0:
    conn = httplib.HTTPConnection("api.twitter.com")
    try:
	conn.request("GET", "/1/" + pre + "/ids.json?user_id=" + user_id)
    except (Exception):
	sys.exit(sys.exc_info())
    r = conn.getresponse()
    sql = "INSERT INTO " + t + " (source_id, target_id, retrieved) VALUES (" + str(user_id) + ", %d, NOW()) "
    if r.status == 200:
	j = simplejson.load(r)
	if len(j) > 0:
	    for x in j:
		#sel = pgconn.query(sql % x)
		try:
		    print pgconn.insert(t, {"source_id": user_id, "target_id": x, "retrieved": "NOW()"})
		except pg.ProgrammingError:
		    print "already exists: " + str(user_id) + "->" + str(x)
		    continue
    else:
	print r.read()
