#!/bin/bash

THRESHOLD=94
DISKS=$(ls -1 /dev/sd??)  # /dev/sdaX
DISKS="${DISKS}
$(ls -d1 /run/user/[0-9]*)" # /run/user/1000
DISKS="${DISKS}
$(ls -1 /dev/mmcblk0??)" # /dev/mmcblk0XX
DISKS="${DISKS}
/tmp"

echo "$DISKS" | while read -r disk
do
    use_perc=$(df -k "$disk" | tail -1 | awk '{print $5}' | tr -d '%')
    if [ "$use_perc" -gt "$THRESHOLD" ]
    then
        /home/aorith/bin/telmsg.sh "$(date +'%Y-%m-%d %H:%M:%S') - WARNING: disk space of $disk
        $(df -h $disk)"
    fi
done


