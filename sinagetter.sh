#!/bin/bash

USAGE="usage: sinagetter.sh [option:1=user_timeline,2=users_show,3=friends,4=followers,5=tags] [user_id] [screen_name(for saving)] [page#] "
SINAUSER="cedricsam@gmail.com"
SINAPASS="LammaIsland"
SINAAPPID="2183853018"
#SINAUSER="YOUR_USERNAME"
#SINAPASS="YOUR_PASSWORD"
#SINAAPPID="YOUR_APPID"
URL1="http://api.t.sina.com.cn/statuses/user_timeline.json?source=${SINAAPPID}&count=200"
URL2="http://api.t.sina.com.cn/users/show.json?source=${SINAAPPID}"
URL3="http://api.t.sina.com.cn/friends/ids.json?source=${SINAAPPID}&count=5000"
URL4="http://api.t.sina.com.cn/followers/ids.json?source=${SINAAPPID}&count=5000"
URL5="http://api.t.sina.com.cn/tags.json?source=${SINAAPPID}"
URL6="http://api.t.sina.com.cn/users/search.json?source=${SINAAPPID}&count=1" # most popular

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
    5)	URL=${URL5};;
    6)	URL=${URL6};;
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
    5) fname="tags-${fname}";;
    6) fname="usersearch-${fname}";;
esac

IF=`rand -M 2`

case $1 in
    1|2|3|4|5)
	#curl -s -u ${SINAUSER}:${SINAPASS} --interface eth${IF} "${URL}&user_id=$2" -o ${fname} ;;
	curl -s -u ${SINAUSER}:${SINAPASS} "${URL}&user_id=$2" -o ${fname} ;;
    6)
	echo ${fname}
	#curl -u ${SINAUSER}:${SINAPASS} --interface eth${IF} "${URL}&q=$2" -o ${fname} ;;
	curl -s -u ${SINAUSER}:${SINAPASS} "${URL}&q=$2" -o ${fname} ;;
esac
