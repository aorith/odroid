#!/bin/bash

THRESHOLD=94
DISKS=$(ls -1 /dev/sd??)  # /dev/sdaX

echo "$DISKS" | while read -r disk
do
    use_perc=$(df -k "$disk" | tail -1 | awk '{print $5}' | tr -d '%')
    if [ "$use_perc" -gt "$THRESHOLD" ]
    then
        /home/aorith/bin/telmsg.sh "$(date +'%Y-%m-%d %H:%M:%S') - WARNING: disk space of $disk
        $(df -h $disk)"
    fi
done


