#!/usr/bin/env python

import sys, os, lucene, threading, time
import pg, mypass
import time, datetime
import csv

class SocialLucene(object):
    """Usage: python SocialLucene <network name> [-d YYYY-MM-DD]"""

    networks = ["uwants", "hkreporter", "discuss", "facebook", "twitter"]
    network = ""
    pgconn = None
    sw = None
    writer = None
    storeDirBase = "/var/data/lucene/"
    storeDir = None
    analyzers = list()

    def __init__(self, network):
	self.network = network	
	smartcn = lucene.SmartChineseAnalyzer(lucene.Version.LUCENE_33)
	#analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_33)
	analyzers = { "smartcn": smartcn }
	self.pgconn = mypass.getConn()
	writerconfig = lucene.IndexWriterConfig(lucene.Version.LUCENE_33, analyzers["smartcn"])
	writerconfig.setWriteLockTimeout(600000L)
	writerconfig.setMaxThreadStates(50)
	writerconfig.setRAMBufferSizeMB(128.0)
	self.storeDir = self.storeDirBase + self.network
	store = lucene.SimpleFSDirectory(lucene.File(self.storeDir))
	self.writer = lucene.IndexWriter(store, writerconfig)

    def indexByDate(self, date_str):
	if self.network == "uwants" or self.network == "hkreporter" or self.network == "discuss":
	    sql = "SELECT * FROM %(network)s_post WHERE date(dbinserted) = '%(date)s' ORDER BY pid " % { "date": date_str, "network": self.network }
    	    try:
    		rows = self.pgconn.query(sql).dictresult()
    	    except pg.ProgrammingError, pg.InternalError:
    		print self.pgconn.error
	    print "Inserting %d rows into Lucene... " % len(rows)
	    count = 0
	    for r in rows:
		count += 1
		if count % 500000 == 0:
		    print count
		    print datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
		pid = r["pid"]
		uid = r["uid"]
		tid = r["tid"]
		title = r["title"]
		content = r["content"]
		floor = r["floor"]
		time_str = r["time"]
		try:
		    t = time.strptime(time_str,"%Y-%m-%d %H:%M:%S")
		    time_str_secs = int(time.mktime(t))
		except:
		    print "Failed converting date %s " % time_str
		    continue
		self.indexHKForumPost(pid, uid, tid, title, content, floor, time_str_secs)
	else:
	    return 0

    def indexHKForumPost(self, pid, uid, tid, title, content, floor, time):
	try:
	    doc = lucene.Document()
	    doc.add(lucene.NumericField("pid", 8, lucene.Field.Store.YES, True).setLongValue(long(pid)))
	    doc.add(lucene.NumericField("uid", 8, lucene.Field.Store.YES, True).setLongValue(long(uid)))
	    doc.add(lucene.NumericField("tid", 8, lucene.Field.Store.YES, True).setLongValue(long(tid)))
	    doc.add(lucene.Field("title", title,
				 lucene.Field.Store.NO,
				 lucene.Field.Index.ANALYZED))
	    doc.add(lucene.Field("content", content,
				 lucene.Field.Store.NO,
				 lucene.Field.Index.ANALYZED))
	    doc.add(lucene.NumericField("floor", lucene.Field.Store.YES, True).setIntValue(floor))
	    doc.add(lucene.NumericField("time", lucene.Field.Store.YES, True).setIntValue(time))
	    self.writer.addDocument(doc)
	except Exception, e:
	    print "Failed in indexWeibos:", e

if __name__ == '__main__':
    networks = ["uwants", "hkreporter", "discuss", "facebook", "twitter"]
    if len(sys.argv) <= 1:
        print SocialLucene.__doc__
        sys.exit(1)
    opt = 0
    network = sys.argv[1]
    if network not in networks:
        print SocialLucene.__doc__
	sys.exit()
    for i in range(2,len(sys.argv)):
	arg = sys.argv[i]
	if arg == "-d" or arg == "--date":
	    if len(sys.argv) > i + 1:
		opt = 1
		insertdate_str = sys.argv[i+1]
		'''
		if len(sys.argv) > i + 2:
		    if ":" in sys.argv[i+2]:
			insertdate_str += " " + sys.argv[i+2]
		'''
		break
    lucene.initVM(lucene.CLASSPATH)
    print 'lucene', lucene.VERSION
    start = datetime.datetime.now()
    indexer = SocialLucene(network=network)
    if opt == 1:
	indexer.indexByDate(insertdate_str)
    try:
	print 'optimizing index'
	indexer.writer.optimize()
	print 'done'
	indexer.writer.close()
    except:
	pass
    end = datetime.datetime.now()
    print end - start
