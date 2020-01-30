#!/bin/bash

#IPLIST=$(grep -v "#" /etc/hosts.deny |grep "ALL:" |cut -d: -f2)
IPLIST=$(sudo iptables -L -n | awk '$1=="REJECT" && $4!="0.0.0.0/0"' | awk '{ print $4 }')
for i in $(echo "$IPLIST")
do
    echo -n "$i - "
    geoiplookup "$i" | cut -d':' -f 2
done

echo "Total: $(echo "$IPLIST" | tr ' ' '\n'| wc -l)"
