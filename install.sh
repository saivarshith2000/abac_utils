#!/bin/bash

# Installer script for ABAC utilities
# Copyright (C) 2021 Hariyala Omakara Naga Sai Varshith

# check if user is root
[ "$UID" -eq 0 ] || { echo "This script must be run as root."; exit 1;}

# check if the ABAC security fs is moounted. This indicates whether kernel
# has enabled and loaded the ABAC LSM
if [ ! -d "/sys/kernel/security/abac/" ]; then
	echo "ABAC LSM is not initialized. Please make sure that the ABAC LSM is enabled and loaded by the kernel"
	exit 1
fi

# install python3-setuptools
if python3 -c "import setuptools" &> /dev/null; then
    echo "Python Setuptools found"
else
    echo "Python Setuptools NOT found"
    echo "Please install python3 setuptools with 'pip install setuptools'"
	exit 1
fi

echo "Installing the ABAC userspace tools and services..."
echo "Creating the shared directory and setting appropriate permissions..."

# create the secured shared abac directory 
mkdir -p /home/secured/
# create a new group 'abac'
groupadd abac
if [ $? -ne 0 ]; then
    echo "Group 'abac' exists already"
fi

set -e
# only users in the abac group can access this directory and its files (note that -R flag)
chgrp -R abac /home/secured/
# recursively change the file modes. 
# Only owners and group members can READ or WRITE to files in this directory
# The sticky bit is set, so only owners can delete/move/rename their files
chmod -R 3770 /home/secured/

echo "Installing the abac cli tool..."
# install the abac cli tool
python3 setup.py install >> /dev/null

echo "Initializing the abac config directory..."
# initialize the abac system
abac init

echo "Installing the abac systemd service..."
cp systemd/abac.service /etc/systemd/system/
systemctl disable abac.service
systemctl enable abac.service
systemctl start abac.service

echo "Installing the abac watcher systemd service..."
cp systemd/abac_watch.service /etc/systemd/system/
systemctl disable abac_watch.service
systemctl enable abac_watch.service
systemctl start abac_watch.service

echo "Installing the abac env systemd service..."
cp systemd/abac_env.service /etc/systemd/system/
systemctl disable abac_env.service
systemctl enable abac_env.service
systemctl start abac_env.service

echo ""
echo "========================="
echo "Installation Successful"
echo "========================="
