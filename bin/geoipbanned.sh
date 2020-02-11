#!/bin/bash

#IPLIST=$(grep -v "#" /etc/hosts.deny |grep "ALL:" |cut -d: -f2)
#IPLIST=$(sudo iptables -L -n | awk '$1=="REJECT" && $4!="0.0.0.0/0"' | awk '{ print $4 }')
IPLIST=$(sudo iptables -L -n | awk '$1=="REJECT" && $4!="0.0.0.0/0"' | awk '{ print $4 }')
# TBD:
# sudo nft list set ip fail2ban f2b-sshd
# sudo nft list set ip fail2ban f2b-apache-custom
for i in $(echo "$IPLIST")
do
    echo -n "$i - "
    geoiplookup "$i" | head -1 | cut -d':' -f 2
done

echo "Total: $(echo "$IPLIST" | tr ' ' '\n'| wc -l)"
