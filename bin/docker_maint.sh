#!/bin/sh
sudo systemctl stop jackett
sudo systemctl stop sonarr
sudo systemctl stop radarr

docker system prune --all -f
docker pull lsioarmhf/jackett
docker pull lsioarmhf/sonarr
docker pull lsioarmhf/radarr

docker network create tv
sleep 10

sudo systemctl start jackett
sudo systemctl start radarr
sudo systemctl start sonarr
