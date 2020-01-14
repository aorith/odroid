#!/bin/sh
echo "Stopping services..."
/home/aorith/bin/docks stop

echo "Pruning docker..."
sudo docker system prune --all -f
echo "Pruning done..."

if [ "$1" = "stop" ]
then
    exit 0
fi

sleep 2

echo "Starting services..."
/home/aorith/bin/docks start
