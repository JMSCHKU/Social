#!/usr/bin/env python

import sys, os
import time, datetime
import csv
import pg
import lucene
import mypass, sinaweibooauth

class SearchSinaWeibo(object):
    """Usage: sinaweibo.search.py [-ds|-de DATE] terms"""

    pgconn = None
    sw = None
    STORE_DIR = "/var/data/lucene/sinaweibo"
    analysers = list()
    searcher = None
    MAX_ITEMS = 500000

    def __init__(self):
	smartcn = lucene.SmartChineseAnalyzer(lucene.Version.LUCENE_33)
	self.analyzers = { "smartcn": smartcn }
	directory = lucene.SimpleFSDirectory(lucene.File(self.STORE_DIR))
	self.searcher = lucene.IndexSearcher(directory, True)
	self.pgconn = mypass.getConn()
	self.sw = sinaweibooauth.SinaWeiboOauth()

    def prepareDates(self, datestring):
	if datestring is None:
	    return None
	try:
	    mydate = time.strptime(datestring, "%Y-%m-%d")
	except ValueError:
	    try:
		mydate = time.strptime(datestring, "%Y-%m-%d %H:%M")
	    except ValueError:
		return None
	return int(time.mktime(mydate))

    def searchWeibos(self, q, created_at_start_secs, created_at_end_secs, user_ids=list()):
	startexec = datetime.datetime.now()
	#q = " ".join(text)
	first = True
	query = lucene.BooleanQuery()
	query.setMaxClauseCount(2097152)
	#q = 'created_at:[%(start)d TO %(end)d] AND (%(q)s)' % { "q": q, "start": created_at_start_secs, "end": created_at_end_secs }
	#q = 'created_at:[%(start)d TO %(end)d]' % { "q": q, "start": created_at_start_secs, "end": created_at_end_secs }
        #query = lucene.QueryParser(lucene.Version.LUCENE_33, "created_at", self.analyzers["smartcn"]).parse(q)
	sorter = lucene.Sort(lucene.SortField("created_at", lucene.SortField.INT, True))
	if len(q) > 0:
	    query.add(lucene.QueryParser(lucene.Version.LUCENE_33, "text", self.analyzers["smartcn"]).parse(q), lucene.BooleanClause.Occur.MUST)
	    if created_at_start_secs is not None and created_at_end_secs is not None:
		dateFilter = lucene.NumericRangeFilter.newIntRange("created_at", created_at_start_secs, created_at_end_secs, True, True)
	else:
	    if created_at_start_secs is not None and created_at_end_secs is not None:
		query.add(lucene.NumericRangeQuery.newIntRange("created_at", created_at_start_secs, created_at_end_secs, True, True), lucene.BooleanClause.Occur.MUST)
	    #dateFilter = lucene.NumericRangeFilter.newIntRange("created_at", created_at_start_secs, created_at_end_secs, True, True)
	topScoreCollector = lucene.TopScoreDocCollector
	if len(user_ids) > 0:
	    user_ids_str = list()
	    numfilters = list()
	    count = 0
	    for x in user_ids:
		count += 1
		user_ids_str.append(str(x))
		#user_ids_str.append("user_id:\"" + str(x) + '"')
		#query.add(lucene.NumericRangeQuery.newIntRange("user_id", x, x, True, True), lucene.BooleanClause.Occur.SHOULD)
		numfilter = lucene.NumericRangeFilter.newIntRange("user_id", x, x, True, True)
		numfilters.append(numfilter)
		#if count > 1000:
		#    break
	    chainedNumFilters = lucene.ChainedFilter(numfilters, lucene.ChainedFilter.OR)
	    cachingChainedNumFilters = lucene.CachingWrapperFilter(chainedNumFilters)
	    if len(q) > 0:
		chain = lucene.ChainedFilter([cachingChainedNumFilters,dateFilter], lucene.ChainedFilter.AND)
	    else:
		chain = cachingChainedNumFilters
	    #query.add(lucene.QueryParser(lucene.Version.LUCENE_33, "user_id", self.analyzers["smartcn"]).parse("(%s)" % " ".join(user_ids_str)), lucene.BooleanClause.Occur.MUST)
	    #query.add(lucene.QueryParser(lucene.Version.LUCENE_33, "user_id", self.analyzers["smartcn"]).parse("user_id:(%s)" % " OR ".join(user_ids_str)), lucene.BooleanClause.Occur.MUST)
	    #topDocs = self.searcher.search(query, chain, self.MAX_ITEMS, sorter)
	    topDocs = self.searcher.search(query, chain, sorter)
	else:
	    if len(q) > 0 and created_at_start_secs is not None and created_at_end_secs is not None:
		topDocs = self.searcher.search(query, dateFilter, self.MAX_ITEMS, sorter)
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
	    id = doc.get("id")
	    user_id = doc.get("user_id")
	    #ids.append(id)
	    hit = { "id": id, "user_id": user_id }
	    hits.append(hit)
	    #ids_str.append(str(id))
	    #if count > self.MAX_ITEMS:
		#break
	out = { "totalhits": topDocs.totalHits, "nb_users": len(user_ids), "ids": ids, "q": q, "hits": hits }
	out["lucene_query_finished"] = long(time.mktime(datetime.datetime.now().timetuple())) * 1000
	if len(user_ids) > 0:
	    out["user_ids"] = user_ids_str
	# Logging
	f = open("/var/data/sinaweibo/searchlog/searchweibos.log","a")
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
