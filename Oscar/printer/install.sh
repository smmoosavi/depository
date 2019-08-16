#!/bin/bash

# set -e
set -x

WORK_DIR=`pwd`

sudo apt-get update

sudo apt-get install -y libusb-1.0-0

sudo apt-get install -y cups

sudo usermod -a -G lpadmin vahid

cd cupsprintdrv-1.1.0_linux/install; sudo ./uninstall.sh; sudo ./install.sh

cd $WORK_DIR

pwd
