#!/bin/bash
source ~/vRMS/bin/activate

cd ~/source/RMS

python ~/source/tackley-tools/dailyPostProc.py -c ~/source/Stations/UK001L/.config 

