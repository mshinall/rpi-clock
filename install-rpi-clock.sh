#!/bin/bash


apt-get update -y
apt-get install -y python-pip
pip install smbus

cp clock-init /etc/init.d
update-rc.d clock-init defaults

cp shutdown-init /etc/init.d
update-rc.d shutdown-init defaults


