#!/bin/bash
# Copyright (C) Mark McIntyre 2025

# Simple script to update RMS and reboot the station
# Should only be run during daytime

cd $HOME/source/RMS
./Scripts/RMS_Update.sh

sudo reboot 
