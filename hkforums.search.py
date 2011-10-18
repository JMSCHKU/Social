#!/usr/bin/env python

import sys, os
import time, datetime
import csv
import pg
import re
import lucene
import mypass, sinaweibooauth

class SearchForums(object):
    """Usage: hkforums.search.py [-ds|-de DATE] terms <forum name>"""

    pgconn = None
    STORE_BASE_DIR = "/var/data/lucene/"
    STORE_DIR = ""
    supported_forums = ["uwants", "discuss", "hkreporter"]
    analysers = list()
    searcher = None
    MAX_ITEMS = 1000
    forum = ""

    def __init__(self, forumname):
	if not forumname in self.supported_forums:
	    sys.exit()
	else:
	    self.forum = forumname
	self.STORE_DIR = self.STORE_BASE_DIR + forumname
	smartcn = lucene.SmartChineseAnalyzer(lucene.Version.LUCENE_33)
	self.analyzers = { "smartcn": smartcn }
	directory = lucene.SimpleFSDirectory(lucene.File(self.STORE_DIR))
	self.searcher = lucene.IndexSearcher(directory, True)
	self.pgconn = mypass.getConn()

    def prepareDates(self, datestring):
	if datestring is None:
	    return None
	try:
	    mydate = time.strptime(datestring, "%Y-%m-%d")
	except ValueError:
	    try:
		mydate = time.strptime(datestring, "%Y-%m-%d %H:%M")
	    except ValueError, TypeError:
		return None
	return int(time.mktime(mydate))

    def searchForums(self, q, time_start_secs, time_end_secs, uids=list(), offset=None, floor=None):
	if offset <> None:
	    try:
		offset = int(offset)
		if offset > self.MAX_ITEMS:
		    self.MAX_ITEMS = offset + 100
	    except:
		pass
	page_start = page_end = None
	if floor <> None and len(floor) > 0:
	    m = re.match(r"(\d+)-?(\d*)", floor)
	    if m <> None:
		page_start = int(m.group(1))
		try:
		    page_end = int(m.group(2))
		except:
		    page_end = page_start
	startexec = datetime.datetime.now()
	first = True
	query = lucene.BooleanQuery()
	query.setMaxClauseCount(2097152)
	sorter = lucene.Sort(lucene.SortField("time", lucene.SortField.INT, True))
	pageFilter = None
	if len(q) > 0:
	    query.add(lucene.QueryParser(lucene.Version.LUCENE_33, "content", self.analyzers["smartcn"]).parse(q), lucene.BooleanClause.Occur.MUST)
	    dateFilter = lucene.NumericRangeFilter.newIntRange("time", time_start_secs, time_end_secs, True, True)
	else:
	    query.add(lucene.NumericRangeQuery.newIntRange("time", time_start_secs, time_end_secs, True, True), lucene.BooleanClause.Occur.MUST)
	if page_start <> None and page_end <> None:
	    pageFilter = lucene.NumericRangeFilter.newIntRange("floor", page_start, page_end, True, True)
	topScoreCollector = lucene.TopScoreDocCollector
	if len(uids) > 0:
	    uids_str = list()
	    numfilters = list()
	    count = 0
	    for x in uids:
		count += 1
		uids_str.append(str(x))
		numfilter = lucene.NumericRangeFilter.newIntRange("uid", x, x, True, True)
		numfilters.append(numfilter)
		#if count > 1000:
		#    break
	    chainedNumFilters = lucene.ChainedFilter(numfilters, lucene.ChainedFilter.OR)
	    cachingChainedNumFilters = lucene.CachingWrapperFilter(chainedNumFilters)
	    if len(q) > 0:
		chain = lucene.ChainedFilter([cachingChainedNumFilters,dateFilter, pageFilter], lucene.ChainedFilter.AND)
	    else:
		chain = cachingChainedNumFilters
	    topDocs = self.searcher.search(query, chain, sorter)
	else:
	    if len(q) > 0 and time_start_secs is not None and time_end_secs is not None:
		if pageFilter is not None:
		    filters = [dateFilter, pageFilter]
		    chainedFilters = lucene.ChainedFilter(filters, lucene.ChainedFilter.AND)
		    topDocs = self.searcher.search(query, chainedFilters, self.MAX_ITEMS, sorter)
		else:
		    topDocs = self.searcher.search(query, dateFilter, self.MAX_ITEMS, sorter)
	    else:
		if pageFilter is not None:
		    topDocs = self.searcher.search(query, pageFilter, self.MAX_ITEMS, sorter)
		else:
		    topDocs = self.searcher.search(query, self.MAX_ITEMS, sorter)
	#return "%(nb)d results found in %(secs)f seconds" %
	ids = list()
	ids_str = list()
	hits = list()
	count = 0
	for scoreDoc in topDocs.scoreDocs:
	    count += 1
	    doc = self.searcher.doc(scoreDoc.doc)
	    id = doc.get("pid")
	    uid = doc.get("uid")
	    tid = doc.get("tid")
	    #ids.append(id)
	    hit = { "pid": id, "uid": uid, "tid": tid }
	    hits.append(hit)
	    #ids_str.append(str(id))
	    #if count > self.MAX_ITEMS:
		#break
	out = { "totalhits": topDocs.totalHits, "nb_users": len(uids), "ids": ids, "q": q, "hits": hits }
	out["lucene_query_finished"] = long(time.mktime(datetime.datetime.now().timetuple())) * 1000
	if len(uids) > 0:
	    out["user_ids"] = uids_str
	# Logging
	f = open("/var/data/hkforums/searchlog/%(forum)s.log" % {"forum": self.forum},"a")
	f.write(datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S") + "\t" + q + "\n")
	f.close()
	endexec = datetime.datetime.now()
	td = endexec - startexec
	microtime = td.microseconds + (td.seconds + td.days * 86400) * 1000000
	secondstime = microtime / 1000000.0
	out["secs"] = secondstime
	print out
	return out

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print SearchSinaWeibo.__doc__
        sys.exit(1)
    inargs = False
    datestart_str = None
    dateend_str = None
    for i in range(1, len(sys.argv)):
	if sys.argv[i].find("-") != 0 and not inargs:
	    i -= 1
	    break
	else:
	    inargs = False
	if sys.argv[i] == "-ds":
	    if len(sys.argv) > i + 1:
		inargs = True
		datestart_str = sys.argv[i+1]
	elif sys.argv[i] == "-de":
	    if len(sys.argv) > i + 1:
		inargs = True
		dateend_str = sys.argv[i+1]
    terms = sys.argv[i+1:len(sys.argv)+1]
    if inargs or len(terms) == 0:# or datestart_str is None:
	print SearchSinaWeibo.__doc__
	sys.exit(1)
    if dateend_str is None:
	dateend_str = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M")
    print terms
    print "date start: " + str(datestart_str)
    print "date end: " + str(dateend_str)
    # Start Lucene
    lucene.initVM(lucene.CLASSPATH)
    print 'lucene', lucene.VERSION
    search = SearchSinaWeibo()
    if datestart_str is None and dateend_str is None:
	search.searchWeibos(terms)
    elif datestart_str is not None:
	search.searchWeibos(terms, search.prepareDates(datestart_str))
    elif dateend_str is not None:
	search.searchWeibos(terms, 0, search.prepareDates(dateend_str))
    else:
	search.searchWeibos(terms, search.prepareDates(datestart_str), search.prepareDates(dateend_str))
