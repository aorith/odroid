#!/bin/bash
if [ "$#" -gt 0 ]; then
	for i in $(seq 1 $#); do
		FILES="`ls -1 /home/aorith/tempsensor/data/${!i}.dat` $FILES"
	done
	FILES=`echo $FILES | tr " " "\n" | sort -n`
else
	FILES=`ls -1 /home/aorith/tempsensor/data/*.dat|sort -n`
fi

cat $FILES | awk -F "[' ',]" '{ total += $3; count++ } END { printf "%.2f\n", total/count }'

