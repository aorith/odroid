#!/bin/bash
BACKUP_PATH="/media/datos/backup"
cd "$BACKUP_PATH" || exit 1

#tempsensor
while [ "$(find "$BACKUP_PATH/tempsensor/" | wc -l)" -ge 40 ]; do
	f=$(find "$BACKUP_PATH/tempsensor/" | tail -1)
	rm -v "$BACKUP_PATH/tempsensor/$f"
	sleep 1
done
