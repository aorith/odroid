#!/bin/bash
docks stop
sudo systemctl stop syncthing
sudo systemctl stop tomcat
sudo systemctl stop bitcoind
sudo systemctl stop transmission-daemon
sudo systemctl stop qbittorrent
#cd /var/www/html/nextcloud
#sudo -u www-data php occ maintenance:mode --on
sudo systemctl stop mariadb
sudo systemctl stop apache2
sudo sync
echo "Rebooting in 5..."
sleep 5
sudo reboot
