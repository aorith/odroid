#!/bin/sh
sudo systemctl stop jackett
sudo systemctl stop sonarr
sudo systemctl stop radarr
sudo systemctl stop lidarr

if [ "$1" = "prune" ]
then
    docker system prune --all -f
fi

if [ "$1" = "stop" ]
then
    exit 0
fi

sleep 2

sudo systemctl start jackett
sudo systemctl start radarr
sudo systemctl start sonarr
sudo systemctl start lidarr
