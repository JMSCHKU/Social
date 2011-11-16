#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pg
import json
import mypass
import time

import sinaweibooauth

if __name__ == "__main__":
    sw = sinaweibooauth.SinaWeiboOauth()
    sw.setToken(sw.sinaweiboOauth["oauth_token"], sw.sinaweiboOauth["oauth_token_secret"]) 
    f = open("/var/data/sinaweibo/mostretweeted/mostretweeted-hk_list1_yesterday.json", "r")
    js = json.loads(f.read())
    for x in js["rts"]:
	print x["id"]
	out = sw.dispatch(9, x["id"])
	print out
	#time.sleep(1)
