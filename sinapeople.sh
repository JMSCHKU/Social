#!/bin/bash

USAGE="usage: sinapeople.sh [1=prov,2=query] [sort=1=latest,2=nbfollowers] [page#] [prov/query] [city]"
SINAUSER="YOUR_EMAIL"
SINAPASS="YOUR_PASSWORD"
SINAAPPID="YOUR_APPID"
URL="http://api.t.sina.com.cn/users/search.json?source=${SINAAPPID}&count=40" # most popular

if [ $# -lt 4 ]
then
    echo ${USAGE}
    exit
fi

case $1 in
    1)	URL="${URL}&province=$4";;
    2)	URL="${URL}&q=$4";;
    *)	echo ${USAGE}; exit
esac

case $2 in
    1|2)URL="${URL}&sort=$2";;
    *)	echo ${USAGE}; exit
esac

URL="${URL}&page=$3"

fname="$4_p$3_`date +%Y%m%d-%H%M`.json"
if [ $# -gt 4 ]
then
    fname="$4-$5_p$3_`date +%Y%m%d-%H%M`.json"
    if [ $1 -eq 1 ]
    then
	URL="${URL}&city=$5"
    fi
fi

case $1 in
    1) fname="searchprov-${fname}";;
    2) fname="search-${fname}";;
esac

echo ${URL}

D1=`date +%N`
D2=`date +%N`
INF="--interface eth`rand -M 2 -s ${D1}`"
if [ `rand -M 2 -s ${D2}` -eq 0 ]; then INF=${INF}:0; fi

curl ${INF} -s -u ${SINAUSER}:${SINAPASS} "${URL}" -o ${fname}
