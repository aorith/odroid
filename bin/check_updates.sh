#!/bin/sh

upd_check() {
	sudo apt update > /tmp/updates.txt
	if grep -q '\-\-upgradable' /tmp/updates.txt; then
		sudo apt list --upgradable > /tmp/upgradable.txt
		/home/aorith/bin/telmsg.sh "$(cat /tmp/upgradable.txt)"
	fi
}


if test -f /tmp/updates.txt; then
	if grep -q '\-\-upgradable' /tmp/updates.txt; then
		sudo apt update > /tmp/updates.txt
		exit 0
	else
		upd_check
	fi
else
	upd_check
fi
