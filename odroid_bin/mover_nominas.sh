#!/bin/bash

RUTA="/media/datos/Syncthing/WORK/99_EMPRESAS/TCDN/TEMP_NOMINAS"
RUTANOMINAS="/media/datos/Syncthing/ARCHIVE/00_Nominas/TransparentCDN"
FICHEROS="$(find ${RUTA} -type f -iname "*.PDF" 2>/dev/null)"

if [[ -z "$FICHEROS" ]]; then
    exit 0
fi

for f in $FICHEROS; do
    fichero="$(basename "$f")"
    year="${fichero%%.*}"
    rutadestino="${RUTANOMINAS}/${year}"
    if [[ ! -d "${rutadestino}" ]]; then
        if ! mkdir "${rutadestino}"; then
            echo "ERROR al crear directorio"
            exit 1
        fi
    fi
    echo "Tratando ${f} ..."
    mv -v "$f" "${rutadestino}/"
done

