#!/bin/bash

if [ "$1" = "start" ]; then
    ( x11vnc -create -env FD_PROG=/usr/bin/fluxbox \
	    -env X11VNC_FINDDISPLAY_ALWAYS_FAILS=1 \
        -env X11VNC_CREATE_GEOM="800x600x16" \
        -gone 'killall Xvfb' \
        -ncache 10 \
        -bg -nopw ) >/dev/null 2>&1
elif [ "$1" = "stop" ]; then
    killall fluxbox
    killall x11vnc
    killall Xvfb
elif [ "$1" = "fake" ]; then
    export DISPLAY=:1
    ( Xvfb :1 -screen 0 800x600x16
    fluxbox
    x11vnc -display :1 -bg -nopw ) >/dev/null 2>&1
fi
