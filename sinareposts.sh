#!/bin/bash

DATADIR=${HOME}/data/sinaweibo/reposts

cd ${DATADIR}

USAGE="usage: sinareposts.sh [post_id] [OPT=max_pages] [OPT=start_page]"
MAXTRIES=10
MAXBLANKS=4
CONSEQ_BLANKS=0

if [ $# -lt 1 ]
then
    echo ${USAGE}
    exit
else
    POSTID=$1
fi

if [ $# -gt 1 ]
then
    MAXP=$2
else
    MAXP=1000
fi

if [ $# -gt 2 ]
then
    STAP=$3
else
    STAP=1
fi

# create a directory for this status
mkdir ${POSTID} &> /dev/null
cd ${POSTID}

# get the original post first
${HOME}/bin/sinasingle.sh ${POSTID}
FI=`ls sina-status-${POSTID}.json | tail -n 1`
${HOME}/bin/sinastorage.py 1 ${FI}

# go through multiple pages
for i in `seq ${STAP} ${MAXP}`
do
    #echo ${POSTID}
    CHECK1=999
    CHECK2=2
    COUNT=0
    while ([ ${CHECK1} -gt 0 ] || [ ${CHECK2} -eq 2 ]) && [ ${COUNT} -lt ${MAXTRIES} ]
    do
	if [ ${COUNT} -gt 0 ] && [ ${COUNT} -lt ${MAXTRIES} ]
	then
	    echo "Trying again... ${COUNT} "
	fi
    	${HOME}/bin/sinagetter.sh 7 ${POSTID} ${POSTID} ${i}
	FI=`ls reposts-${POSTID}-${i}_*.json | tail -n 1`
	CHECK1=`wc -l ${FI} | cut -f1 -d" " `
	CHECK2=`wc -m ${FI} | cut -f1 -d" " `
	let COUNT=${COUNT}+1
    done
    # fail if we are exceeding the number of missed calls to the API (receiving error messages)
    if ([ ${COUNT} -eq ${MAXTRIES} ] || [ ${COUNT} -gt ${MAXTRIES} ]) && [ ${CHECK1} -gt 0 ]
    then
	echo "Error: missed too many times"
	break
    fi
    # count the consecutive "[]", then stop if too many of them
    if [ ${CHECK1} -eq 0 ] && [ ${CHECK2} -gt 2 ]
    then
	CONSEQ_BLANKS=0
    else
    	let CONSEQ_BLANKS=${CONSEQ_BLANKS}+1
	if [ ${CONSEQ_BLANKS} -gt ${MAXBLANKS} ]
	then
	    echo "Error: too many empty results, so we must be done..."
	    break
	fi
	continue
    fi
    ${HOME}/bin/sinastorage.py 1 ${FI}
    echo ${i} ${CHECK1} ${CHECK2}
    rm ${FI}
done
