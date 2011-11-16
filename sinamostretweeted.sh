#!/bin/bash

WWWDIR=${HOME}/www-social/sinaweibo
DATADIR=${HOME}/data/sinaweibo/mostretweeted

cd ${DATADIR}

TODAY=`date +%Y-%m-%d`
NOWSHORT=`date +%Y%m%d-%H%M`
HALFHOUR=`date -d"30 minutes ago" +%Y%m%d-%H%M`
LASTHOUR=`date -d"last hour" +%Y%m%d-%H%M`
THREEHOURSAGO=`date -d"3 hours ago" +%Y%m%d-%H%M`
FOURHOURSAGO=`date -d"4 hours ago" +%Y%m%d-%H%M`
SIXHOURSAGO=`date -d"6 hours ago" +%Y%m%d-%H%M`
EIGHTHOURSAGO=`date -d"8 hours ago" +%Y%m%d-%H%M`
TWELVEHOURSAGO=`date -d"12 hours ago" +%Y%m%d-%H%M`
echo start: `date +%Y%m%d-%H%M`

EXTOPT=""
PREFIX=""
case $1 in
    1)	EXTOPT="-maxfol";PREFIX="maxfol_";;
    2)	EXTOPT="-l";PREFIX="list";;
esac

if [ $# -gt 1 ]
then
    if [ $1 -eq 2 ]
    then
	EXTOPT="${EXTOPT} $2"; PREFIX="${PREFIX}$2_"
    fi
fi

if [[ $0 == *short* ]]
then
    if [[ $0 == *very.short* ]]
    then
	fname_intervals="intervals.very.short.txt"
    else
	fname_intervals="intervals.short.txt"
    fi
else
    fname_intervals="intervals.txt"
fi

echo ${fname_intervals}

while read x
do
    #divid=`echo ${x} | cut -d, -f1`
    fileid=${PREFIX}`echo ${x} | cut -d, -f2`
    #title=`echo ${x} | cut -d, -f3`
    datewhen=`echo ${x} | cut -d, -f4`

    INTERVAL=`date -d"${datewhen}" +%Y-%m-%d`
    echo ${datewhen}: `date +%Y%m%d-%H%M`

    echo "First pass..."

    ${HOME}/bin/sinamostretweeted_firstpass.py ${INTERVAL} -o mostretweeted-hk_${fileid}_${NOWSHORT} -c ${EXTOPT}

    head -n 200 mostretweeted-hk_${fileid}_${NOWSHORT}.csv > mostretweeted-hk_${fileid}_${NOWSHORT}_200.csv
    mv mostretweeted-hk_${fileid}_${NOWSHORT}_200.csv mostretweeted-hk_${fileid}_${NOWSHORT}.csv

    # enter the statuses that have are not in the db yet
    for i in `head -n 200 mostretweeted-hk_${fileid}_${NOWSHORT}.csv | grep ",,$" | cut -d, -f1`
    do
	echo $i
	#${HOME}/bin/sinasingle.sh ${i}
	#${HOME}/bin/sinastorage.py 1 sina-status-${i}.json
	#rm sina-status-${i}.json
	${HOME}/bin/sinaweibo2.oauth.py $i -ss -v -c > out_${fileid}_${NOWSHORT}.tmp
	WC=`grep "status code = 403" out_${fileid}_${NOWSHORT}.tmp | wc -l | cut -d" " -f1`
	if [ ${WC} -gt 0 ]
	then
	    ${HOME}/bin/sinaweibo.oauth.py $i -ss -v -c
	fi
    done

    echo "Second pass..."

    # now get an update list of statuses and find the missing users
    ${HOME}/bin/sinamostretweeted_secondpass.py mostretweeted-hk_${fileid}_${NOWSHORT}.csv -o mostretweeted-hk_${fileid}_${NOWSHORT}_users -no -c

    # get the users not in the DB
    for i in `head -n 200 mostretweeted-hk_${fileid}_${NOWSHORT}_users.csv | grep ",$" | cut -d, -f2 `
    do
	${HOME}/bin/sinaweibo2.oauth.py $i -u -v > out_${fileid}_${NOWSHORT}.tmp
	WC=`grep "status code = 403" out_${fileid}_${NOWSHORT}.tmp | wc -l | cut -d" " -f1`
	if [ ${WC} -gt 0 ]
	then
	    ${HOME}/bin/sinaweibo.oauth.py $i -u -v
	fi
	#${HOME}/bin/sinagetter.sh 2 ${i} ${i}
	#FI=`ls userinfo-${i}_*.json | tail -n 1`
	#${HOME}/bin/sinastorage.py 2 ${FI}
	#rm ${FI}
    done
    rm out_${fileid}_${NOWSHORT}.tmp

    ${HOME}/bin/sinamostretweeted_secondpass.py mostretweeted-hk_${fileid}_${NOWSHORT}.csv -o mostretweeted-hk_${fileid}_${NOWSHORT}

    head -n 40 mostretweeted-hk_${fileid}_${NOWSHORT}.csv | cut -d, -f1 > most-reposted-ids-${fileid}.txt
    rm mostretweeted-hk_${fileid}_${NOWSHORT}.csv
    rm mostretweeted-hk_${fileid}_${NOWSHORT}_users.csv

    mv mostretweeted-hk_${fileid}_${HALFHOUR}.json reports
    mv mostretweeted-hk_${fileid}_${HALFHOUR}_users.json reports
    mv mostretweeted-hk_${fileid}_${LASTHOUR}.json reports
    mv mostretweeted-hk_${fileid}_${LASTHOUR}_users.json reports
    mv mostretweeted-hk_${fileid}_${THREEHOURSAGO}.json reports
    mv mostretweeted-hk_${fileid}_${THREEHOURSAGO}_users.json reports
    mv mostretweeted-hk_${fileid}_${FOURHOURSAGO}.json reports
    mv mostretweeted-hk_${fileid}_${FOURHOURSAGO}_users.json reports
    mv mostretweeted-hk_${fileid}_${SIXHOURSAGO}.json reports
    mv mostretweeted-hk_${fileid}_${SIXHOURSAGO}_users.json reports
    mv mostretweeted-hk_${fileid}_${EIGHTHOURSAGO}.json reports
    mv mostretweeted-hk_${fileid}_${EIGHTHOURSAGO}_users.json reports
    mv mostretweeted-hk_${fileid}_${TWELVEHOURSAGO}.json reports
    mv mostretweeted-hk_${fileid}_${TWELVEHOURSAGO}_users.json reports
    rm mostretweeted-hk_${fileid}.json
    ln -s mostretweeted-hk_${fileid}_${NOWSHORT}.json mostretweeted-hk_${fileid}.json

done < ${fname_intervals}

echo end: `date +%Y%m%d-%H%M`
