#!/bin/sh

if [ -n "$DISPLAY" -a -f /usr/sbin/redhat-config-network-gui ]; then
    exec /usr/sbin/redhat-config-network-gui
else
    exec /usr/sbin/redhat-config-network-tui
fi
