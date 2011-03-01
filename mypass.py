# -*- coding: utf-8 -*-

import pg

def getConn():
    return pg.DB('DB_NAME', '127.0.0.1', 5432, None, None, 'DB_USER', 'DB_PASS')

def getTwitterOauth():
    return { "consumer_key": "YOUR_CONSUMER_KEY", "consumer_secret": "YOUR_CONSUMER_SECRET",\
    "oauth_token": "YOUR_OAUTH_TOKEN", "oauth_token_secret": "YOUR_OAUTH_SECRET" }

def getFacebookOauth():
    return { "app_id": "YOUR_APPID", "access_token": "YOUR_TOKEN" }

def getFacebookUserId():
    return "YOUR_FBID"
