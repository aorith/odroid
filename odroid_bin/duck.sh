#!/bin/bash

THRESHOLD=72000
TOKEN=$(sed -n '1p' "$HOME/secret/duckdns.txt")
DOM1=$(sed -n '2p' "$HOME/secret/duckdns.txt")
DOM2=$(sed -n '3p' "$HOME/secret/duckdns.txt")
DOMS=( ${DOM1} ${DOM2} )

for d in "${DOMS[@]}"
do
    output=$(curl -k -s "https://www.duckdns.org/update?domains=$d&token=$TOKEN&ip=")

    if [ "$output" != "OK" ]
    then
        # if flag exist and is older then THRESHOLD seconds -> send alert
        if [ -e "/tmp/fail-$d" ]
        then
            if [ "$(( $(date +"%s") - $(stat -c "%Y" "/tmp/fail-$d") ))" -gt "$THRESHOLD" ]
            then
                /home/aorith/bin/telmsg.sh "$(date +'%Y%m%d %H:%M:%S') -> duckdns failed on $d"
            fi
        else
            touch "/tmp/fail-$d"
        fi
    else
        rm -f "/tmp/fail-$d"
    fi
done

