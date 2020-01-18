#!/bin/bash
cd "$(dirname "$0")" || exit 1
if [ -e /tmp/update_graphs ]
then
    ./graphs/graphs.py
    /home/aorith/githome/odroid/bin/telmsg.sh "graphs updated"
    sudo rm /tmp/update_graphs
fi
