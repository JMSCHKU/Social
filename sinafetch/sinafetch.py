#!/usr/bin/env python
# -*- coding: utf-8 -*-

## using APIClient from https://github.com/michaelliao/sinaweibopy

from weibo import APIClient
import weibo
import mypass
import sys
import pg
import httplib
import time
import string

#import oauth2 as oauth
import pprint

import datetime
import csv
import types

import unittest
import socket

#import lucene
#import sinaweibolucene

import argparse

import re
import os

class API():
    sinaweiboOauth = mypass.getSinaWeiboOauth()
    max_api_misses = 6
    pgconn = None
    toleranceNotToBeginning = 5 # in fetching timelines, break from loop when toleranceNotToBeginning consecutive statuses already exist in the DB
    toleranceNotToBeginningLong = 150 # for reposts
    max_gotall_count = 3
    api_wait_secs = 5
    max_api_misses_half = 3
    max_api_misses = 3 ## reduced from 6
    max_reposts_pages = max_comments_pages = 1000
    max_reposts_blanks = max_comments_blanks = 3
    max_reposts_tries = max_comments_tries = 3
    usage = "sinafetch.py [id or file with ids] [primary opts] [sec opts]"
    rp_dir = "/var/data/sinaweibo/rp"
    comments_dir = "/var/data/sinaweibo/comments"
    reposts_dir = "/var/data/sinaweibo/reposts"
    timelines_dir = "/var/data/sinaweibo/timelines"
    timeline_ids = list()
    verbose = False
    getall = False
    force_screenname = False
    checkonly = False
    doupdate = False
    saveRP = False
    rt = False # Don't store the retweet
    index = False
    indexer = None
    doublecheck = False # If we get a blank timeline, it may just be an error, so we log it
    cliparser = argparse.ArgumentParser(description="Sina Weibo API to DB tool")

    def __init__(self):
	self.setClient()
	self.setToken(self.sinaweiboOauth['access_token'], self.sinaweiboOauth['expires_in'])
	self.initParser()

    def setClient(self):
        self.api2 = APIClient(app_key=self.sinaweiboOauth['app_key'], app_secret=self.sinaweiboOauth['app_secret'], redirect_uri=self.sinaweiboOauth['redirect_uri'])

    def setToken(self, access_token, expires_in):
        self.api2.set_access_token(access_token, expires_in)
    
    def reqToken(self, access):
        self.api2.set_access_token(self.sinaweiboOauth['access_token'], self.sinaweiboOauth['expires_in'])


    def getAtt(self, obj, key):
        try:
            return obj.__getattribute__(key)
        except Exception, e:
            return None
    def setAtt(self, obj, key, value):
        try:
            return obj.__setattribute__(key, value)
        except Exception, e:
            return None

    def fixdate(self, textdate):
        '''
        fix the date(string) returned from Sina to the standard format 
        '''
        textdate = re.sub(r' \+....', '', textdate) # kill the +0800, not supported by strptime
        datedt = datetime.datetime.strptime(textdate, "%a %b %d %H:%M:%S %Y")
        return datedt.strftime("%Y-%m-%d %H:%M:%S")
    #def get_rateLimit(self):

    def get_apistatus(self):
        ratelimit = self.api2.account.rate_limit_status.get()
        print ratelimit
        
    def get_status(self, id, getUser=False, toDB=False):
        #time_db = 0
        #time_db_u = 0
        start_time_api = time.time()
        api_misses = 0
        while api_misses < self.max_api_misses:
            try:
                status = self.api2.statuses.show.get(id=id)
                break
            except weibo.APIError as e: ## Need more exception handling, and warned by > Python 2.6.
                print e.message
                api_misses += 1
                if api_misses >= self.max_api_misses:
                    return { "id": id, "err_msg": e.message } ## aka toxicbar
                if e.message is not None and  ("target weibo does not exist" in e.message.lower() or "permission denied" in e.message.lower()):
                    permission_denied = False
                    if ("permission denied" in e.message.lower()):
                        permission_denied = True
                    return { 'id': id, "error_msg": e.message, "deleted": True, "Permission_denied": permission_denied }
                time.sleep(self.api_wait_secs * 1)
        time_api = time.time() - start_time_api
        # status is just a glorified dict, not an object like weibopy2
        # So don't need to use getAtt
        row = self.status_to_row(status) 
        return row

    def status_to_row(self, status):
        x = dict()
        x["created_at"] = self.fixdate(status["created_at"])
        for a in ["text", "source", "location", "thumbnail_pic", "bmiddle_pic", "original_pic", "screen_name", "in_reply_to_screen_name"]:
            try:
                att = status[a]
            except:
                att = None
            try:
                x[a] = att.encode("utf8")
            except:
                x[a] = att
        for a in ["id", "in_reply_to_user_id", "in_reply_to_status_id", "truncated", "reposts_count", "comments_count", "attitudes_count", "mlevel", "deleted"]:
            try:
                x[a] = status[a]
            except:
                x[a] = None
        try:
            rts = status['retweeted_status']['id']
        except:
            rts = None # This message is original
        try:
            rts_user_id = status['retweeted_status']['user']['id']
        except:
            rts_user_id = None
        if rts is not None:
            if self.rt:
                rt_dict = status['retweeted_status']
                if rt_dict['created_at'] is not None:
                    x['rt'] = self.status_to_row(rt_dict)
            x['retweeted_status'] = rts
        if rts_user_id is not None:
            x['retweeted_status_user_id'] = rts_user_id
        try:
            user_id = status['user']['id']
        except:
            user_id = None
        try:
            screen_name = status['user']['screen_name'].encode("utf-8")
        except:
            screen_name = None
        if user_id is not None:
            x['user_id'] = user_id
        if screen_name is not None:
            x['screen_name'] = screen_name
        try:
            geo = status['geo']
            coord = geo["coordinates"]
        except:
            geo = None
        if geo is not None and coord is not None and len(coord) >0:
            lat = coord[0]
            lng = coord[1]
            wkt_point = "POINT(" + str(lng) + " " + str(lat) + ")"
	    #print wkt_point
	    x["geo"] = "SRID=4326;" + wkt_point
	return x

    def get_usertimeline(self, user_id, count=100, page=1):
        start_time_api = time.time()
        api_misses = 0
        while api_misses < self.max_api_misses:
            try:
                timeline = self.api2.statuses.user_timeline.get(uid=user_id, count=count, page=page)
                break
            except Exception as e:
                print e.message
                api_misses += 1
                if api_misses >= self.max_api_misses:
                    return { "id": user_id, "err_msg": e.message }
        return timeline

    def get_userinfo(self, user_id):
        start_time_api = time.time()
        api_misses = 0
        while api_misses < self.max_api_misses:
            try:
                userinfo = self.api2.users.show.get(uid=user_id)
                break
            except Exception as e:
                print e.message
                api_misses += 1
                if api_misses >= self.max_api_misses:
                    return { "id": id, "err_msg": e.message }
        return userinfo


    def user_to_row(self, userinfo):
	x = dict()
	try:
            x["created_at"] = self.fixdate(userinfo["created_at"])
	    #x["created_at"] = self.getAtt(user, "created_at").strftime("%Y-%m-%d %H:%M:%S")
	except:
	    #print self.getAtt(user, "id")
	    #print self.getAtt(user, "created_at")
	    x["created_at"] = None
	x["retrieved"] = "NOW()"
	for a in ["name", "screen_name", "location", "description", "profile_image_url", "url", "avatar_large", "verified_reason"]:
	    try:
		att = userinfo[a]
		x[a] = att.encode("utf8")
	    except:
		x[a] = None
	for a in ["id", "province", "city", "domain", "gender", "followers_count", "friends_count", "favourites_count", \
"time_zone", "profile_background_image_url", "profile_use_background_image", "allow_all_act_msg", "geo_enabled", \
"verified", "following", "statuses_count", "allow_all_comment", "bi_followers_count", "deleted", "verified_type", "lang", "online_status"]:
            try:
                x[a] = userinfo[a]
            except:
                x[a] = None
	return x

    #def punch_row_DB(self, row, typerow, pgconn):
        


    def dispatch(self, opt, id, output_counts=False):
        if opt == 1:
        ### doomsday mode: a combined user and usertimeline fetching
        ### will only get user detail when statuses == []
            timeline = self.get_usertimeline(id)
            #print timeline['total_number']
            ## if no error
            if long(timeline['total_number']) > 0 and len(timeline['statuses']) > 0:
                msg_id = list()
                user_punched = False
                for status in timeline['statuses']:
                    row = self.status_to_row(status)  ## TODO: push row to DB
                    if not user_punched:
                        userinfo = status['user'] ## user_to_row it and punch to DB if needed
                        print self.user_to_row(userinfo)
                        user_punched = True
                    #if 'retweeted_status_user_id' in row.keys():
                        ###
                    #     rt_userinfo = status['retweeted_status']['user'] ## optionally also punch it also to DB
                    #     print self.status_to_row(rt_userinfo)
                    msg_id.append(row['id'])
                out = { 'msg_id': msg_id } ### return a list of all weibo id from timeline
            elif long(timeline['total_number']) > 0 and len(timeline['statuses']) == 0:
                ### blank timeline can be error, need to double check.
                out = None
            else:
                ### TODO: Confirmed Empty timeline, check the user info
                out = self.user_to_row(self.get_userinfo(id))
        elif opt == 9:
            out = self.get_status(id, getUser = True)
            ### will it be better if we put the row into the DB here?
            ### if err_msg in out, and if deleted = True, update the DB for the deleted and permission_denied field
            ### else it is a valid row, put into DB as new record
        else:
            out = None
        return out

    class ParseAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
	    #print '%r %r %r' % (namespace, values, option_string)
	    if option_string == "-ut" or option_string == "-doom" or option_string == "--doomsday-mode":
		setattr(namespace, "opt", 1)
	    if option_string == "-ss":
		setattr(namespace, "opt", 9)

    def initParser(self):
	self.cliparser.add_argument("id", metavar="ID", type=int, help="an ID")
	self.cliparser.add_argument("-ss", action=self.ParseAction, nargs=0)
	self.cliparser.add_argument("-ut", action=self.ParseAction, nargs=0)
	args = self.cliparser.parse_args()
	print args

if __name__ == "__main__":
    api = API()

