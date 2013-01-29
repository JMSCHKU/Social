NB_API_KEYS = 4

def getSinaWeiboOauth2(keyindex=None):
    try:
	keyindex = int(keyindex)
    except:
	keyindex = None
    if keyindex is not None:
	x = keyindex
    else:
	x = int(random.random() * NB_API_KEYS)

    outobj = dict()
    if x == 1:
	outobj = { "app_key": "NUMERICAL_ID_OF_APP", "app_secret": "APP_SECRET","redirect_uri": "SPECIFIED_REDIRECT_URI", "access_token": "ACCESS_TOKEN", "expires_in": 1516443798 } # The expiration is an integer of seconds since epoch
    elif x == 2:
	outobj = { "app_key": "NUMERICAL_ID_OF_APP", "app_secret": "APP_SECRET","redirect_uri": "SPECIFIED_REDIRECT_URI", "access_token": "ACCESS_TOKEN", "expires_in": 0 } 
    elif x == 3:
	outobj = { "app_key": "NUMERICAL_ID_OF_APP", "app_secret": "APP_SECRET","redirect_uri": "SPECIFIED_REDIRECT_URI", "access_token": "ACCESS_TOKEN", "expires_in": 0 } 
    else:
	outobj = { "app_key": "NUMERICAL_ID_OF_APP", "app_secret": "APP_SECRET","redirect_uri": "SPECIFIED_REDIRECT_URI", "access_token": "ACCESS_TOKEN", "expires_in": 0 } 

    outobj["keyindex"] = x
    outobj["nb_api_keys"] = NB_API_KEYS

    return outobj

