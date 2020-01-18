#!/bin/bash
cd "$(dirname "$0")" || (touch /home/aorith/tempsensor.failed; exit 1)
if [ ! -e /dev/hidraw1 ]
then
    MSG="$(date +'%Y%m%d %H:%M:%S') :: /dev/hidraw1 not found. Check USB."
    echo "$MSG" >> /home/aorith/tempsensor.alert
    /home/aorith/githome/odroid/bin/telmsg.sh "$MSG"
    exit 1
fi
OUTLINE=$(sudo hid-query /dev/hidraw1 0x01 0x80 0x33 0x01 0x00 0x00 0x00 0x00|grep -A1 ^Response|tail -1)

OUTNUM=$(echo "$OUTLINE" | tr -d ' \t')

# TEMP
HEX4=${OUTNUM:4:4}
DVAL=$(( 16#$HEX4 ))
CTEMP=$(bc <<< "scale=2; $DVAL/100")
#HUMIDITY
HEX4=${OUTNUM:8:4}
DVAL=$(( 16#$HEX4 ))
HUM=$(bc <<< "scale=2; $DVAL/100")

CPUTEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
CPUTEMP=$(bc <<< "scale=2; $CPUTEMP/1000")

sqlite3 ./data/temperature.db "INSERT INTO temperature VALUES (datetime('now', 'localtime'), $CTEMP, $HUM, $CPUTEMP);"
