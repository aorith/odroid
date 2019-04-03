#!/bin/bash

TOKEN=$(sed -n '1p' "$HOME/secret/duckdns.txt")
DOM1=$(sed -n '2p' "$HOME/secret/duckdns.txt")
DOM2=$(sed -n '3p' "$HOME/secret/duckdns.txt")

output=$(curl -k -s "https://www.duckdns.org/update?domains=$DOM1&token=$TOKEN&ip=")
if [ "$output" != "OK" ]
then
    # if flag exist and is older than seconds below, send alert
    if [ -e "/tmp/fail-$DOM1" ]
    then
        if [ "$(( $(date +"%s") - $(stat -c "%Y" "/tmp/fail-$DOM1") ))" -gt "43200" ]
        then
            /home/aorith/bin/telmsg.sh "$(date +'%Y%m%d %H:%M:%S') -> duckdns failed on $DOM1"
        fi
    else
        touch "/tmp/fail-$DOM1"
    fi
else
    rm -f "/tmp/fail-$DOM1"
fi

output=$(curl -k -s "https://www.duckdns.org/update?domains=$DOM2&token=$TOKEN&ip=")
if [ "$output" != "OK" ]
then
    # if flag exist and is older than seconds below, send alert
    if [ -e "/tmp/fail-$DOM2" ]
    then
        if [ "$(( $(date +"%s") - $(stat -c "%Y" "/tmp/fail-$DOM2") ))" -gt "43200" ]
        then
            /home/aorith/bin/telmsg.sh "$(date +'%Y%m%d %H:%M:%S') -> duckdns failed on $DOM2"
        fi
    else
        touch "/tmp/fail-$DOM2"
    fi
else
    rm -f "/tmp/fail-$DOM2"
fi

