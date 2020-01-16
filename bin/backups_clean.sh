#!/bin/bash
BACKUP_PATH="/media/datos/backup"
cd "$BACKUP_PATH" || exit 1

# tempsensor - Delete backups when more than 40 present
max_backups=40
directory="tempsensor"
while [ "$(find "$BACKUP_PATH/$directory/" | wc -l)" -ge $max_backups ]; do
	f=$(find "$BACKUP_PATH/$directory/" | tail -1)
	rm -v "$f"
	sleep 1
done
