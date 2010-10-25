#!/bin/bash

USAGE="usage: sinagetter.sh [option:1=user_timeline,2=users_show,3=friends,4=followers] [user_id] [screen_name(for saving)] [page#] "
SINAUSER="YOUR_EMAIL_ADDRESS"
SINAPASS="YOUR_PASSWORD"
SINAAPPID="YOUR_APPID"
URL1="http://api.t.sina.com.cn/statuses/user_timeline.json?source=${SINAAPPID}&count=200"
URL2="http://api.t.sina.com.cn/users/show.json?source=${SINAAPPID}"
URL3="http://api.t.sina.com.cn/friends/ids.json?source=${SINAAPPID}&count=5000"
URL4="http://api.t.sina.com.cn/followers/ids.json?source=${SINAAPPID}&count=5000"

if [ $# -lt 3 ]
then
    echo ${USAGE}
    exit
fi

case $1 in
    1)	URL=${URL1};;
    2)	URL=${URL2};;
    3)	URL=${URL3};;
    4)	URL=${URL4};;
esac

if [ $# -gt 3 ]
then
    fname="$3-$4_`date +%Y%m%d-%H%M`.json"
    case $1 in
	1)	URL="${URL}&page=$4";;
	3|4)	URL="${URL}&cursor=$4";;
    esac
else
    fname="$3_`date +%Y%m%d-%H%M`.json"
fi

case $1 in
    1) fname="statuses-${fname}";;
    2) fname="userinfo-${fname}";;
    3) fname="friends-${fname}";;
    4) fname="followers-${fname}";;
esac

curl -u ${SINAUSER}:${SINAPASS} "${URL}&user_id=$2" -o ${fname}
