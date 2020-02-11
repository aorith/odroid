#!/bin/bash
now=$(date +'%Y.%m.%d %H:%M:%S')
msg="$now -"
open_sesame() {
    if sudo iptables -A OPEN_SESAME -p tcp --dport 22 -j ACCEPT;
    then
        msg="knock.sh: $(sudo tail -4 /var/log/knockd.log | grep "OPEN SESAME")"
    else
        msg="knock.sh: $msg error opening ssh"
    fi
    /home/aorith/bin/telmsg.sh "$msg"
}

close_the_door() {
    if sudo iptables -D OPEN_SESAME -p tcp --dport 22 -j ACCEPT;
    then
        msg="knock.sh: $msg ssh is closed"
    else
        msg="knock.sh: $msg error closing ssh"
    fi
    /home/aorith/bin/telmsg.sh "$msg"
}

check_fw() {
    if ! sudo iptables -L |grep -q "INPUT (policy DROP";
    then
        /home/aorith/bin/telmsg.sh "Careful; Input policy is not set correcly"
    fi
}

# run
check_fw
[[ "$1" = "open" ]] && open_sesame && exit 0
[[ "$1" = "close" ]] && close_the_door && exit 0

exit 33
