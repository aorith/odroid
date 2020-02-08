#!/bin/bash

now=$(date +'%Y.%m.%d %H:%M:%S')
msg="$now -"
open_sesame() {
    if sudo ufw allow from any to any port 22 proto tcp comment 'allow global ssh';
    then
        msg="$(sudo tail -4 /var/log/knockd.log | grep "OPEN SESAME")"
    else
        msg="$msg error opening ssh"
    fi
    /home/aorith/bin/telmsg.sh "$msg"
}

close_the_door() {
    if sudo ufw delete allow from any to any port 22 proto tcp comment 'allow global ssh';
    then
        msg="$msg ssh is closed"
    else
        msg="$msg error closing ssh"
    fi
    /home/aorith/bin/telmsg.sh "$msg"
}

check_ufw() {
    if ! sudo ufw --force enable;
    then
        /home/aorith/bin/telmsg.sh "UFW failed to start!"
    fi
}

# run
check_ufw
[[ "$1" = "open" ]] && open_sesame && exit 0
[[ "$1" = "close" ]] && close_the_door && exit 0

exit 33
