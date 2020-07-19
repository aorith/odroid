#!/bin/bash
now=$(date +'%Y.%m.%d %H:%M:%S')
header="$(basename $0) $now"

telmsg () {
    /home/aorith/odroid_bin/telmsg.sh "$header
    $1"
}

open_sesame() {
    if sudo iptables -A OPEN_SESAME -p tcp --dport 22 -j ACCEPT;
    then
        msg="$(sudo tail -4 /var/log/knockd.log | grep "OPEN SESAME")"
    else
        msg="error opening ssh"
    fi
    telmsg "$msg"
}

close_the_door() {
    if sudo iptables -D OPEN_SESAME -p tcp --dport 22 -j ACCEPT;
    then
        msg="ssh is closed"
    else
        msg="error closing ssh"
    fi
    telmsg "$msg"
}

check_fw() {
    if ! sudo iptables -L |grep -q "INPUT (policy DROP";
    then
        telmsg "Careful; Input policy is not set correcly"
    fi
}

# run
check_fw
[[ "$1" = "open" ]] && open_sesame && exit 0
[[ "$1" = "close" ]] && close_the_door && exit 0

exit 33
