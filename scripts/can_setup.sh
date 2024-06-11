#! /usr/bin/bash

# Make sure the script runs with super user privileges
[ "$UID" -eq 0 ] || exec sudo bash "$0" "$@"

# Set up CAN interface
ip link set can0 type can bitrate 250000
ifconfig can0 txqueuelen 65536
ifconfig can0 up