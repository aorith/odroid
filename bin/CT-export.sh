#!/bin/bash

CTFILE="/media/datos/Syncthing/SYNC_STUFF/CherryTree/NOTES.ctb"
OUTDIR="/media/datos/Syncthing/SYNC_STUFF/CherryTree/"

# xvfb-run creates a virtual X server env
xvfb-run /usr/bin/cherrytree -x ${OUTDIR} ${CTFILE} -w

