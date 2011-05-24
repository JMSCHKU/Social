#!/bin/bash

# Not used anymore. Superseded by sinaweibo.oauth.py

USAGE="usage: sinagetter.sh [option:1=user_timeline,2=users_show,3=friends,4=followers,5=tags,6=mostpopularusers,7=reposts,8=comments] [user_id] [screen_name(for saving)] [page#] "
SINAUSER="YOUR_EMAIL"
SINAPASS="YOUR_PASSWORD"
SINAAPPID="YOUR_APPID"
URL1="http://api.weibo.com/statuses/user_timeline.json?source=${SINAAPPID}&count=200"
URL2="http://api.weibo.com/users/show.json?source=${SINAAPPID}"
URL3="http://api.weibo.com/friends/ids.json?source=${SINAAPPID}&count=5000"
URL4="http://api.weibo.com/followers/ids.json?source=${SINAAPPID}&count=5000"
URL5="http://api.weibo.com/tags.json?source=${SINAAPPID}"
URL6="http://api.weibo.com/users/search.json?source=${SINAAPPID}&count=1" # most popular
URL7="http://api.weibo.com/statuses/repost_timeline.json?source=${SINAAPPID}&count=200" # reposts
URL8="http://api.weibo.com/statuses/comments.json?source=${SINAAPPID}&count=200" # reposts

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
    7)	URL=${URL7};;
    8)	URL=${URL8};;
esac

if [ $# -gt 3 ]
then
    fname="$3-$4_`date +%Y%m%d-%H%M`.json"
    case $1 in
	1|7|8)	URL="${URL}&page=$4";;
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
    7) fname="reposts-${fname}";;
    8) fname="comments-${fname}";;
esac

# For network load balancing
D1=`date +%N`
D2=`date +%N`
INF="--interface eth`rand -M 2 -s ${D1}`"
if [ `rand -M 2 -s ${D2}` -eq 0 ]; then INF=${INF}:0; fi

case $1 in
    1|2|3|4|5)
	curl ${INF} -s -u ${SINAUSER}:${SINAPASS} "${URL}&user_id=$2" -o ${fname} ;;
    6)
	curl ${INF} -s -u ${SINAUSER}:${SINAPASS} "${URL}&q=$2" -o ${fname} ;;
    7|8)
	curl ${INF} -s -u ${SINAUSER}:${SINAPASS} "${URL}&id=$2" -o ${fname} ;;
esac
