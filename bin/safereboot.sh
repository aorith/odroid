#!/bin/bash
docks stop
sudo systemctl stop syncthing
sudo systemctl stop tomcat
sudo systemctl stop bitcoind
sudo systemctl stop transmission-daemon
sudo systemctl stop qbittorrent
sudo sync
echo "Rebooting in 5..."
sleep 5
sudo reboot
