#!/bin/bash

# BACKUPS

## JOPLIN

JOPLIN_BIN="$HOME/.joplin-bin/bin/joplin"
JOPLIN_BACKUP_FOLDER="/media/datos/Syncthing/SYNC_STUFF/Joplin-Backups"

if [ "$1" = "joplin" ]
then
    cd "${JOPLIN_BACKUP_FOLDER}" || (echo "ERROR: can't cd to $JOPLIN_BACKUP_FOLDER" && exit 1)
    NPM_CONFIG_PREFIX=$HOME/.joplin-bin npm update -g joplin markdown-it
    $JOPLIN_BIN --log-level error sync
    export_name="$(date +'%Y%m%d%H%M%S').jex"
    $JOPLIN_BIN --log-level error export --format jex "${JOPLIN_BACKUP_FOLDER}/${export_name}"
    xz "${export_name}" || (echo "ERROR: couldn't compress ${JOPLIN_BACKUP_FOLDER}/${export_name}" && exit 1)
fi

######################################################

# CLEANING

# which folders to clean
# folder|max_files|extension_of_backups
# files exceeding the max_files number will be deleted
cfg="""
$JOPLIN_BACKUP_FOLDER|14|.jex.xz
"""

IFS="|"
is_number='^[0-9]+$'
line=0
echo "$cfg" | while read -r folder max_files extension
do
    # checks
    let "line=line+1"
    [[ -z "$folder" || -z "$max_files" || -z "$extension" ]] && continue
    [[ ! -d "$folder" || ! "$max_files" =~ $is_number ]] && echo "ERROR: check cfg line $line" && continue

    max_loops=2
    cd "$folder" || (echo "ERROR: can't cd to $folder" && exit 1)
    while [ "$(find "$folder/" -type f -name "*${extension}" | wc -l)" -gt $max_files ]; do
	    f=$(find "$folder/" -type f -name "*${extension}" -print | LC_ALL=C sort -n | head -1)
	    rm -v "$f"
        let "max_loops=max_loops-1"
        [[ "$max_loops" -le 0 ]] && exit 0
	    sleep 1
    done
done

