#!/usr/bin/env python

import sys, os, lucene, threading, time
import pg, mypass, sinaweibooauth
import time, datetime
import csv

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexSinaWeibo(object):
    """Usage: python IndexSinaWeibo [-d YYYY-MM-DD]"""

    pgconn = None
    sw = None
    writer = None
    storeDir = "/var/data/lucene/sinaweibo"
    analyzers = list()
    ticker = None

    def __init__(self):
	smartcn = lucene.SmartChineseAnalyzer(lucene.Version.LUCENE_33)
	#analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_33)
	analyzers = { "smartcn": smartcn }
	self.pgconn = mypass.getConn()
	self.sw = sinaweibooauth.SinaWeiboOauth()
	if not os.path.exists(self.storeDir):
	    os.mkdir(self.storeDir)
	store = lucene.SimpleFSDirectory(lucene.File(self.storeDir))
	writerconfig = lucene.IndexWriterConfig(lucene.Version.LUCENE_33, analyzers["smartcn"])
	writerconfig.setWriteLockTimeout(600000L)
	writerconfig.setMaxThreadStates(50)
	writerconfig.setRAMBufferSizeMB(128.0)
	self.writer = lucene.IndexWriter(store, writerconfig)
	#self.writer.setMaxFieldLength(1048576)
	#self.ticker = Ticker()
	#threading.Thread(target=self.ticker.run).start()
	#self.writer.optimize()
	#self.writer.close()
	#self.ticker.tick = False

    def indexWeibosByIsoDate(self, yeariso, weekiso):
	yw = { "yeariso": yeariso, "weekiso": weekiso }
	print "Fetching weibos inserted on year %(yeariso)d and week %(weekiso)d " % yw
	sql = "SELECT id, created_at, user_id, text FROM rp_sinaweibo_y%(yeariso)dw%(weekiso)d WHERE date(dbinserted) IS NULL ORDER BY id " % yw
	try:
	    rows = self.pgconn.query(sql).dictresult()
	except pg.ProgrammingError, pg.InternalError:
	    print self.pgconn.error
	    return { "msg": self.pgconn.error }
	print "Inserting %d rows into Lucene... " % len(rows)
	count = 0
	for r in rows:
	    count += 1
	    if count % 500000 == 0:
		print count
		print datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
	    tid = r["id"]
	    text = r["text"]
	    user_id = r["user_id"]
	    created_at = r["created_at"]
	    try:
		t = time.strptime(created_at,"%Y-%m-%d %H:%M:%S")
		created_at_secs = int(time.mktime(t))
	    except:
		print "Failed converting date %s " % created_at
		continue
	    self.indexWeibo(tid, text, user_id, created_at_secs)

    def indexWeibosByInsertDate(self, insertdate_str):
	try:
	    insertdate = datetime.datetime.strptime(insertdate_str, "%Y-%m-%d")
	except ValueError:
	    errmsg = "Invalid date: %s " % insertdate_str
	    return { "msg": errmsg }
	print "Fetching weibos inserted on %s" % insertdate_str
	sql = "SELECT id, created_at, user_id, text FROM rp_sinaweibo WHERE date(dbinserted) = '%s' ORDER BY id " % insertdate_str
	try:
	    rows = self.pgconn.query(sql).dictresult()
	except pg.ProgrammingError, pg.InternalError:
	    print self.pgconn.error
	    return { "msg": self.pgconn.error }
	print "Inserting %d rows into Lucene... " % len(rows)
	count = 0
	for r in rows:
	    count += 1
	    if count % 500000 == 0:
		print count
		print datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
	    tid = r["id"]
	    text = r["text"]
	    user_id = r["user_id"]
	    created_at = r["created_at"]
	    try:
		t = time.strptime(created_at,"%Y-%m-%d %H:%M:%S")
		created_at_secs = int(time.mktime(t))
	    except:
		print "Failed converting date %s " % created_at
		continue
	    self.indexWeibo(tid, text, user_id, created_at_secs)

    def indexWeibosByIdFromDB(self, tid):
	print "adding weibo #%d" % tid
	try:
	    rps = self.sw.getRangePartitionByIds([tid])
	    sw_tables_arr = list()
	    for x in rps:
		yw = x.split(",")
		year = int(yw[0])
		week = int(yw[1])
		sw_tables_arr.append("SELECT id, created_at, user_id, text FROM rp_sinaweibo_y%(year)dw%(week)d y%(year)dw%(week)d" % { "year": year, "week": week })
	    sw_tables = " UNION ".join(sw_tables_arr)
	    sw_tables = "(%s)" % sw_tables
	    res = self.pgconn.query("SELECT id, created_at, user_id, text FROM %(sw_tables)s s WHERE id = %(tid)d " % { "sw_tables": sw_tables, "tid": tid })
	except pg.ProgrammingError, pg.InternalError:
    	    print self.pgconn.error
	    return self.pgconn.error
	r = res.dictresult()
	if len(r) <= 0:
	    return "Weibo doesn't exist"
	text = r[0]["text"]
    	user_id = r[0]["user_id"]
	created_at = r[0]["created_at"]
	try:
	    t = time.strptime(created_at,"%Y-%m-%d %H:%M:%S")
	    created_at_secs = int(time.mktime(t))
	except:
	    return "Failed converting date "
	self.indexWeibo(tid, text, user_id, created_at_secs)

    def indexWeibosFromCSV(self, fpath):
	f = open(fpath, "rU")
	#dialect = csv.Sniffer().sniff(f.read(4096))
	#f.seek(0)
	#cr = csv.reader(f, dialect)
	#cr = csv.DictReader(f, dialect=dialect, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar="\\", lineterminator="\n")
	cr = csv.DictReader(f, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar="\\", lineterminator="\n")
	count = 0
	for x in cr:
	    count += 1
	    if count % 500000 == 0:
		print count
		print datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
	    try:
		t = time.strptime(x["created_at"],"%Y-%m-%d %H:%M:%S")
		created_at_secs = int(time.mktime(t))
	    except:
		print "Failed converting date: %s " % x["created_at"]
		continue
	    try:
		self.indexWeibo(x["id"], x["text"], x["user_id"], created_at_secs)
	    except Exception as e:
		print e
		print x["id"]
		print x["text"]
		continue
	self.writer.optimize()
	#self.writer.close()
	#self.ticker.tick = False

    def indexWeibosFromRows(self, rows):
	'''Inserts rows in the index by timeline rows'''
	for x in rows:
	    created_at_secs = None
	    try:
		t = time.strptime(x["created_at"],"%Y-%m-%d %H:%M:%S")
		created_at_secs = int(time.mktime(t))
	    except:
		continue
	    self.indexWeibo(x["id"], x["text"], x["user_id"], created_at_secs)
	self.writer.optimize()
	self.writer.close()
	#self.ticker.tick = False

    def indexWeibo(self, tid, text, user_id, created_at):
	try:
	    doc = lucene.Document()
	    doc.add(lucene.NumericField("id", 8, lucene.Field.Store.YES, True).setLongValue(long(tid)))
	    doc.add(lucene.Field("text", text,
				 lucene.Field.Store.NO,
				 lucene.Field.Index.ANALYZED))
	    doc.add(lucene.NumericField("user_id", lucene.Field.Store.YES, True).setIntValue(int(user_id)))
	    doc.add(lucene.NumericField("created_at", lucene.Field.Store.YES, True).setIntValue(created_at))
	    self.writer.addDocument(doc)
	except Exception, e:
	    print "Failed in indexWeibos:", e

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print IndexSinaWeibo.__doc__
        sys.exit(1)
    opt = 0
    for i in range(1,len(sys.argv)):
	arg = sys.argv[i]
	if arg == "-d" or arg == "--date":
	    if len(sys.argv) > i + 1:
		opt = 1
		insertdate_str = sys.argv[i+1]
		break
	if arg == "-yw" or arg == "--year-week":
	    if len(sys.argv) > i + 2:
		opt = 2
		yeariso = int(sys.argv[i+1])
		weekiso = int(sys.argv[i+2])
		break
    lucene.initVM(lucene.CLASSPATH)
    print 'lucene', lucene.VERSION
    start = datetime.datetime.now()
    indexer = IndexSinaWeibo()
    if opt == 1:
	indexer.indexWeibosByInsertDate(insertdate_str)
    if opt == 2:
	indexer.indexWeibosByIsoDate(yeariso, weekiso)
    #indexer.indexWeibosByIdFromDB(3352644673101184)
    #indexer.indexWeibosByIdFromDB(3352116729032709)
    #indexer.indexWeibosByIdFromDB(3352742815828213)
    #indexer.indexWeibosFromCSV("/var/data/lucene/y2011w33.csv")
    #indexer.indexWeibosFromCSV("/var/data/lucene/y2011w34.csv")
    #indexer.indexWeibosFromCSV("/var/data/lucene/y2011w35.csv")
    #indexer.indexWeibosFromCSV("/var/data/lucene/y2011w36.csv")
    #indexer.ticker.tick = False
    try:
	print 'optimizing index'
	indexer.writer.optimize()
	print 'done'
	indexer.writer.close()
    except:
	pass
    end = datetime.datetime.now()
    print end - start
