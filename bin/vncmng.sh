#!/bin/bash

if [ "$1" = "start" ]; then
    x11vnc -create -env FD_PROG=/usr/bin/fluxbox \
	    -env X11VNC_FINDDISPLAY_ALWAYS_FAILS=1 \
        -env X11VNC_CREATE_GEOM=${1:-800x600x16} \
        -gone 'killall Xvfb' \
        -bg -nopw >/dev/null 2>&1
elif [ "$1" = "stop" ]; then
    killall fluxbox >/dev/null 2>&1
    killall x11vnc >/dev/null 2>&1
    killall Xvfb >/dev/null 2>&1
elif [ "$1" = "fake" ]; then
    export DISPLAY=:1
    Xvfb :1 -screen 0 800x600x16 >/dev/null 2>&1
    fluxbox  >/dev/null 2>&1
    x11vnc -display :1 -bg -nopw >/dev/null 2>&1
fi
