#!/bin/bash

# This is an important script that checks the number of members of a group, attendees of an event or fans of a page
# Based on that number, we figure whether this entity is worth "following" (see watch.facebook.sh)

cd ${HOME}/data/facebook/watch/
LIMIT=600
LIMIT1=800
THRESHOLD=100
YESTERDAY=`date -d"yesterday" +%Y-%m-%d`
BEFORE=`date -d"3 days ago" +%Y-%m-%d`
LASTHOUR=`date -d"last hour" +"%Y-%m-%d %H:%M:%S"`
GRACEPERIOD=`date -d"36 hours ago" +"%Y-%m-%d %H:%M:%S"`
EVENTENDED=`date -d"last week" +"%Y-%m-%d %H:%M:%S"`
RETRIEVEDTOOOLD=`date -d"1 month ago" +"%Y-%m-%d %H:%M:%S"`

# Correction for Taiwanese groups, events or pages
echo "Cleaning Taiwanese groups, events or pages..."
echo "Doing groups..."
SQLGTAIWAN="UPDATE facebook_groups g SET watching = FALSE WHERE watching IS NOT FALSE AND (lower(name) ILIKE '%taiwan%' OR name LIKE '%臺%' OR name LIKE '%台灣%' OR name LIKE '%台北%' OR name ILIKE '%taipei%' OR name LIKE '%高雄%' OR name LIKE '%台中%' OR name LIKE '%台南%' OR name LIKE '%新竹%' OR name LIKE '%花蓮%') AND name NOT LIKE '%香港%' AND lower(name) NOT ILIKE '%hong%kong%' "
psql -h 127.0.0.1 -U jmsc -c "${SQLGTAIWAN}"
SQLGTAIWAN="UPDATE facebook_groups g SET watching = FALSE WHERE watching IS NOT FALSE AND (link ilike '%.tw%' or link ilike '%tw.%') and link not ilike '%.hk%' and link not ilike '%hongkong%' "
psql -h 127.0.0.1 -U jmsc -c "${SQLGTAIWAN}"
echo "Doing events..."
SQLETAIWAN="UPDATE facebook_events e SET watching = FALSE WHERE watching IS NOT FALSE AND (description ILIKE '%taiwan%' OR description LIKE '%臺%' OR description LIKE '%台灣%' OR description LIKE '%台北%' OR description ILIKE '%taipei%' OR description LIKE '%高雄%' OR description LIKE '%台中%' OR description LIKE '%台南%' OR description LIKE '%新竹%' OR description LIKE '%花蓮%') AND description NOT LIKE '%香港%' AND description NOT ILIKE '%hong%kong%' "
echo ${SQLETAIWAN}
psql -h 127.0.0.1 -U jmsc -c "${SQLETAIWAN}"
SQLETAIWAN="UPDATE facebook_events e SET watching = FALSE WHERE watching IS NOT FALSE AND (location ILIKE '%taiwan%' OR location LIKE '%臺%' OR location LIKE '%台灣%' OR location LIKE '%台北%' OR location ILIKE '%taipei%' OR location LIKE '%高雄%' OR location LIKE '%台中%' OR location LIKE '%台南%' OR location LIKE '%新竹%' OR location LIKE '%花蓮%') AND location NOT LIKE '%香港%' AND location NOT ILIKE '%hong%kong%' "
echo ${SQLETAIWAN}
psql -h 127.0.0.1 -U jmsc -c "${SQLETAIWAN}"
SQLETAIWAN="UPDATE facebook_events e SET watching = FALSE WHERE watching IS NOT FALSE AND (name ILIKE '%taiwan%' OR name LIKE '%臺%' OR name LIKE '%台灣%' OR name LIKE '%台北%' OR name ILIKE '%taipei%' OR name LIKE '%高雄%' OR name LIKE '%台中%' OR name LIKE '%台南%' OR name LIKE '%新竹%' OR name LIKE '%花蓮%') AND name NOT LIKE '%香港%' AND lower(name) NOT ILIKE '%hong%kong%' "
echo ${SQLETAIWAN}
psql -h 127.0.0.1 -U jmsc -c "${SQLETAIWAN}"
echo "Doing pages..."
SQLPTAIWAN="UPDATE facebook_pages p SET watching = FALSE WHERE watching IS NOT FALSE AND (name ILIKE '%taiwan%' OR name LIKE '%臺%' OR name LIKE '%台灣%' OR name LIKE '%台北%' OR name ILIKE '%taipei%' OR name LIKE '%高雄%' OR name LIKE '%台中%' OR name LIKE '%台南%' OR name LIKE '%新竹%' OR name LIKE '%花蓮%') AND name NOT LIKE '%香港%' AND lower(name) NOT ILIKE '%hong%kong%' "
psql -h 127.0.0.1 -U jmsc -c "${SQLPTAIWAN}"
SQLGTAIWAN="UPDATE facebook_pages g SET watching = FALSE WHERE watching IS NOT FALSE AND (link ilike '%.tw%' or link ilike '%tw.%') and link not ilike '%.hk%' and link not ilike '%hongkong%' "
psql -h 127.0.0.1 -U jmsc -c "${SQLGTAIWAN}"

# correct ended event
echo "Cleaning finished events..."
SQLEENDED="UPDATE facebook_events e SET watching = FALSE WHERE end_time < '${EVENTENDED}' AND watching IS NOT FALSE"
psql -h 127.0.0.1 -U jmsc -c "${SQLEENDED}"
echo "Cleaning groups and pages retrieved a while ago..."
SQLGOLD="UPDATE facebook_groups g SET watching = FALSE WHERE retrieved < '${RETRIEVEDTOOOLD}' AND watching IS NULL"
psql -h 127.0.0.1 -U jmsc -c "${SQLGOLD}"
SQLPOLD="UPDATE facebook_pages p SET watching = FALSE WHERE retrieved < '${RETRIEVEDTOOOLD}' AND watching IS NULL"
psql -h 127.0.0.1 -U jmsc -c "${SQLPOLD}"


echo "Creating lists of IDs to check..."

# watching = null (have not been checked)
SQLG="\\copy (select id, 'group', 'notwatching' from facebook_groups g where watching is null and retrieved < '${GRACEPERIOD}' order by retrieved desc limit ${LIMIT}) to 'groups_checkwatching_null.txt' csv "
SQLE="\\copy (select id, 'event', 'notwatching' from facebook_events e where watching is null and retrieved < '${GRACEPERIOD}' order by retrieved desc limit ${LIMIT}) to 'events_checkwatching_null.txt' csv "
SQLP="\\copy (select id, 'page', 'notwatching' from facebook_pages p where watching is null and retrieved < '${GRACEPERIOD}' order by retrieved desc limit ${LIMIT}) to 'pages_checkwatching_null.txt' csv "
psql -h 127.0.0.1 -U jmsc -c "${SQLG}"
psql -h 127.0.0.1 -U jmsc -c "${SQLE}"
psql -h 127.0.0.1 -U jmsc -c "${SQLP}"

# watching = null (have been checked)
SQLGNY="\\copy (select eid, 'event', 'notwatchingyet' from (select eid from facebook_events_watch group by eid) as ew left join facebook_events e on ew.eid = e.id where watching is null limit ${LIMIT1}) to 'events_checkwatching_notyet.txt' csv "
SQLGNY="\\copy (select gid, 'group', 'notwatchingyet' from (select gid from facebook_groups_watch group by gid) as gw left join facebook_groups g on gw.eid = g.id where watching is null limit ${LIMIT1}) to 'groups_checkwatching_notyet.txt' csv "
SQLGNY="\\copy (select pid, 'page', 'notwatchingyet' from (select pid from facebook_pages_watch group by pid) as pw left join facebook_pages p on pw.pid = p.id where watching is null limit ${LIMIT1}) to 'pages_checkwatching_notyet.txt' csv "
psql -h 127.0.0.1 -U jmsc -c "${SQLGNY}"
psql -h 127.0.0.1 -U jmsc -c "${SQLENY}"
psql -h 127.0.0.1 -U jmsc -c "${SQLPNY}"

# watching = true (have not been checked)
SQLGW="\\copy (select id, 'group', 'watching' from facebook_groups g where watching is true order by retrieved desc limit ${LIMIT}) to 'groups_checkwatching.txt' csv "
SQLEW="\\copy (select id, 'event', 'watching' from facebook_events e where watching is true order by retrieved desc limit ${LIMIT}) to 'events_checkwatching.txt' csv "
SQLPW="\\copy (select id, 'page', 'watching' from facebook_pages p where watching is true order by retrieved desc limit ${LIMIT}) to 'pages_checkwatching.txt' csv "
psql -h 127.0.0.1 -U jmsc -c "${SQLGW}"
psql -h 127.0.0.1 -U jmsc -c "${SQLEW}"
psql -h 127.0.0.1 -U jmsc -c "${SQLPW}"

# HK-related keywords
HKKWDIR=/var/data/facebook/hongkong
rm hkkw_facebook_events.txt hkkw_facebook_pages.txt events_hongkong.txt pages_hongkong.txt
sort -un ${HKKWDIR}/hkkw_facebook_events_*.txt > hkkw_facebook_events.txt
sort -un ${HKKWDIR}/hkkw_facebook_pages_*.txt > hkkw_facebook_pages.txt
while read i
do
    echo `echo ${i} | sed 's/\r//g'`,event,hongkong >> events_hongkong.txt
done < hkkw_facebook_events.txt
while read i
do
    echo `echo ${i} | sed 's/\r//g'`,page,hongkong >> pages_hongkong.txt
done < hkkw_facebook_pages.txt

rm all_checkwatching.txt
cat events_hongkong.txt pages_hongkong.txt *_checkwatching_null.txt *_checkwatching_notyet.txt *_checkwatching.txt >> all_checkwatching.txt

# reinitialise newly watching file
rm newlywatching.csv
rm hongkongwatching.csv

while read i
do
    ID=`echo ${i} | cut -d, -f1 `
    TYPE=`echo ${i} | cut -d, -f2 `
    WATCHING=`echo ${i} | cut -d, -f3 `
    TYPE1=`echo ${TYPE} | head -c1 `
    echo ${ID} ${TYPE} ${WATCHING}
    SQLPW="SELECT * FROM facebook_${TYPE}s_watch WHERE ${TYPE1}id = ${ID} %and_date% ORDER BY retrieved DESC LIMIT 1 "
    if [ "${TYPE}" == "event" ]
    then
	SQLPW="SELECT eid, retrieved, attending_count FROM facebook_${TYPE}s_watch WHERE ${TYPE1}id = ${ID} %and_date% ORDER BY retrieved DESC LIMIT 1 "
    fi
    psql -h 127.0.0.1 -U jmsc -F, -tAc "`echo -e \"${SQLPW}\" | sed \"s/%and_date%/AND retrieved <\= \'${BEFORE}\'/g\"`" > ${ID}_watch_before.csv
    #psql -h 127.0.0.1 -U jmsc -F, -tAc "`echo -e \"${SQLPW}\" | sed \"s/%and_date%/AND retrieved <\= \'${YESTERDAY}\'/g\"`" > ${ID}_watch_yesterday.csv
    BEFOREWATCH=`wc -l ${ID}_watch_before.csv | cut -d' ' -f1 `
    #YESTERDAYWATCH=`wc -l ${ID}_watch_yesterday.csv | cut -d' ' -f1 `

    # this block was copied from watch.facebook.sh
    # it updates the local version of the entity and adds a row in the watch table
    case ${TYPE} in
	group)
	    ${HOME}/bin/facebook.graph.py ${ID} -t group -a -u -q
	    # from DB, get the members count and store it in the watch table
	    SQLGC="INSERT INTO facebook_groups_watch (gid, members_count, retrieved) SELECT ${ID}, COUNT(*), NOW() FROM facebook_users_groups WHERE gid = ${ID} GROUP BY gid "
	    psql -h 127.0.0.1 -U jmsc -c "${SQLGC}"
	;;
	event)
	    ${HOME}/bin/facebook.graph.py ${ID} -t event -a -u -q
	    # from DB, get the attendees status
	    SQLEC="SELECT rsvp_status, COUNT(*) FROM facebook_users_events WHERE eid = ${ID} GROUP BY rsvp_status ORDER BY rsvp_status "
	    psql -h 127.0.0.1 -U jmsc -F, -tAc "${SQLEC}" > ${ID}_check.csv
	    ATTENDING=`( echo 0 && grep attending ${ID}_check.csv | cut -d, -f2 ) | tail -n1` # if attending not found, we only echo 0, and head -n 0 will get it
	    DECLINED=`( echo 0 && grep declined ${ID}_check.csv | cut -d, -f2 ) | tail -n1`
	    NOTREPLIED=`( echo 0 && grep not_replied ${ID}_check.csv | cut -d, -f2 ) | tail -n1`
	    UNSURE=`( echo 0 && grep unsure ${ID}_check.csv | cut -d, -f2 ) | tail -n1`
	    # save to watch table
	    SQLECINS="INSERT INTO facebook_events_watch (eid, attending_count, declined_count, notreplied_count, unsure_count, retrieved) VALUES (${ID}, ${ATTENDING}, ${DECLINED}, ${NOTREPLIED}, ${UNSURE}, NOW()) "
	    psql -h 127.0.0.1 -U jmsc -c "${SQLECINS}"
	    rm ${ID}_check.csv
	;;
	page)
	    ${HOME}/bin/facebook.graph.py ${ID} -t page -u -q
	    # from DB, get the fan count
	    SQLPC="SELECT fan_count FROM facebook_pages WHERE id = ${ID} "
	    psql -h 127.0.0.1 -U jmsc -F, -tAc "${SQLPC}" > ${ID}_check.csv
	    COUNT=`cat ${ID}_check.csv`
	    SQLPCINS="INSERT INTO facebook_pages_watch (pid, fan_count, retrieved) VALUES (${ID}, ${COUNT}, NOW()) "
	    psql -h 127.0.0.1 -U jmsc -c "${SQLPCINS}"
	    rm ${ID}_check.csv
	;;
    esac

    # get the latest that we just entered (or entered in the last hour)
    psql -h 127.0.0.1 -U jmsc -F, -tAc "`echo -e \"${SQLPW}\" | sed \"s/%and_date%/AND retrieved >\= \'${LASTHOUR}\'/g\"`" > ${ID}_watch_last.csv
    NEWWATCH=`wc -l ${ID}_watch_last.csv | cut -d' ' -f1 `

    # in case we have two columns in the watch table two days apart
    if [ "${BEFOREWATCH}" == 1 ]
    then
	if [ "${NEWWATCH}" == 1 ] || [ ${WATCHING} == "watching" ]
	then
	    IS_WATCHING=''
	    OLDDATE=`cat ${ID}_watch_before.csv | cut -d, -f2`
	    NEWDATE=`cat ${ID}_watch_last.csv | cut -d, -f2`
	    OLDCOUNT=`cat ${ID}_watch_before.csv | cut -d, -f3`
	    NEWCOUNT=`cat ${ID}_watch_last.csv | cut -d, -f3`
	    #echo ${OLDCOUNT} ${OLDDATE}
	    #echo ${NEWCOUNT} ${NEWDATE}
	    echo ${OLDCOUNT} ${OLDDATE} -==- ${NEWCOUNT} ${NEWDATE}
	    if [ "${OLDCOUNT}" == 0 ] 
	    then
		continue
	    fi
	    X=`echo "scale=2; ${NEWCOUNT} / ${OLDCOUNT}" | bc`
	    d=`echo "${NEWCOUNT} - ${OLDCOUNT}" | bc`
	    if [ "${WATCHING}" == "watching" ]
	    then
		echo "watching is true"
		if [ "`echo "$X > 1.2 " | bc `" == 1 ] || [ "`echo "${NEWCOUNT} > 499 " bc `" == 1 ]
		then
		    IS_WATCHING=1
		fi
		if [ "`echo "$X < 1.02 " | bc `" == 1 ] && [ "${NEWCOUNT}" -gt ${THRESHOLD} ]
		then
		    IS_WATCHING=0
		fi
		if [ "`echo "$d < 10 " | bc `" == 1 ] && [ "${NEWCOUNT}" -gt 1000 ]
		then
		    IS_WATCHING=0
		fi
	    elif [ "${WATCHING}" == "notwatching" ] || [ "${WATCHING}" == "notwatchingyet" ]
	    then
		echo "watching is null"
		if [ "`echo "$X <= 1.03 " | bc `" == 1 ]
		then
		    IS_WATCHING=0
		fi
		if [ "`echo "$d < -10 " | bc `" == 1 ]
		then
		    IS_WATCHING=0
		fi
		if [ "`echo "$X > 1.15 " | bc `" == 1 ] && [ "${NEWCOUNT}" -gt ${THRESHOLD} ]
		then
		    IS_WATCHING=1
		fi
		if [ "`echo "$d > 30 " | bc `" == 1 ]
		then
		    IS_WATCHING=1
		fi
		if [ "${OLDCOUNT}" -lt ${THRESHOLD} ] && [ "${NEWCOUNT}" -lt ${THRESHOLD} ]
		then
		    IS_WATCHING=''
		fi
		# for newly added
		if [ "${IS_WATCHING}" == 1 ]
		then
		    echo ${ID},${TYPE} >> newlywatching.csv
		fi
	    elif [ "${WATCHING}" == "hongkong" ]
	    then
		echo "hong kong"
		if [ "`echo "$X > 1 " | bc `" == 1 ]
		then
		    IS_WATCHING=1
		fi
		if [ "`echo "$d > 0 " | bc `" == 1 ]
		then
		    IS_WATCHING=1
		fi
		# for hongkongwatching
		if [ "${IS_WATCHING}" == 1 ]
		then
		    echo ${ID},${TYPE} >> hongkongwatching.csv
		fi
	    fi
	    if [ "${IS_WATCHING}" == 0 ]
	    then
		SQLNOTWATCHING="UPDATE facebook_${TYPE}s SET watching = false WHERE id = ${ID} "
		echo ${SQLNOTWATCHING}
		psql -h 127.0.0.1 -U jmsc -c "${SQLNOTWATCHING}"
	    elif [ "${IS_WATCHING}" == 1 ]
	    then
		SQLWATCHING="UPDATE facebook_${TYPE}s SET watching = true WHERE id = ${ID} "
		echo ${SQLWATCHING}
		psql -h 127.0.0.1 -U jmsc -c "${SQLWATCHING}"
	    fi
	fi
    fi

    # cleanup
    rm ${ID}_watch_before.csv
    #rm ${ID}_watch_yesterday.csv
    rm ${ID}_watch_last.csv

done < all_checkwatching.txt

rm *_watch_before.csv
rm *_watch_last.csv
