#!/bin/bash

THRESHOLD=95


for i in 1 2
do
    use_perc=$(df -k "/dev/sda$i" | tail -1 | awk '{print $5}' | tr -d '%')
    if [ "$use_perc" -gt "$THRESHOLD" ]
    then
        /home/aorith/bin/telmsg.sh "$(date +'%Y-%m-%d %H:%M:%S') - WARNING: disk space of /dev/sda$i
        $(df -h /dev/sda$i)"
    fi
done


