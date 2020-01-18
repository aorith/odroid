#!/bin/bash
DATA="/home/aorith/tempsensor/data/*.dat"

if [ "$#" -lt 2 ]; then
	DATA_D=`cat $DATA | cut -d" " -f1 |  uniq`

	if [ "$#" -eq 1 ]; then
		DATA_D=`echo $DATA_D| tr " " "\n" | grep "$1"`
	fi

	for f in $DATA_D;
	do
		grep -h "$f" $DATA | awk -F "[' ',]" '{ date1 = $1; total += $3; count++ } END { printf "%s,%.2f\n", date1, total/count }'
	done
fi

if [ "$#" -eq 2 ]; then
	DATA="/home/aorith/tempsensor/data/`date +'%Y'`.dat"
	DATA_D="$1"
	MAXHOUR="$2"
	STARTHOUR=`grep 20181012 $DATA | head -1 | cut -d' ' -f2 | cut -d',' -f1`
	STARTHOUR="${STARTHOUR:0:4}"
	awk "/^$DATA_D $STARTHOUR.+$/,/^$DATA_D $MAXHOUR.+$/" "/home/aorith/tempsensor/data/$(date +'%Y').dat" | awk -F "[' ',]" '{ date1 = $1; total += $3; count++ } END { printf "%s,%.2f\n", date1, total/count }'
fi
