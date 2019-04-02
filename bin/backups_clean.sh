#!/bin/bash
BACKUP_PATH="/media/datos/backup"
cd $BACKUP_PATH

#tempsensor
while [ `ls $BACKUP_PATH/tempsensor/|wc -l` -ge 40 ]; do
	f=`ls -1t $BACKUP_PATH/tempsensor/ | tail -1`
	rm -v $BACKUP_PATH/tempsensor/$f
	sleep 1
done
