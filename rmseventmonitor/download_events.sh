#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

dt=$1
mkdir -p $here/archives/$dt

rsync -avz gmn.uwo.ca:/home/uk*/files/event_monitor/*${dt}*.bz2 $here/archives/$dt
rsync -avz gmn.uwo.ca:/home/be000h/files/event_monitor/${dt}*.bz2 $here/archives/$dt
rsync -avz gmn.uwo.ca:/home/ie000j/files/event_monitor/${dt}*.bz2 $here/archives/$dt
rsync -avz gmn.uwo.ca:/home/ie0004/files/event_monitor/${dt}*.bz2 $here/archives/$dt

cd $here/archives/$dt

for f in *.bz2 ; do tar -xvf $f  ; done
if [ -d UKMON ] ; then
    sites=$(ls -1 UKMON)
    for site in $sites ; do
        cams=$(ls -1 UKMON/$site)
        for cam in $cams ; do 
            if [ -d ./$cam ] ; then rm -Rf $cam ; fi
            mv -f UKMON/$site/$cam .
        done
    done
    rm -Rf UKMON
fi 
if [ -d NEMETODE ] ; then
    sites=$(ls -1 NEMETODE)
    for site in $sites ; do
        cams=$(ls -1 NEMETODE/$site)
        for cam in $cams ; do 
            if [ -d ./$cam ] ; then rm -Rf $cam ; fi
            mv -f NEMETODE/$site/$cam .
        done
    done
    rm -Rf NEMETODE
fi 
if [ -d "UKMON,NEMETODE" ] ; then
    sites=$(ls -1 "UKMON,NEMETODE")
    for site in $sites ; do
        cams=$(ls -1 "UKMON,NEMETODE/$site")
        for cam in $cams ; do 
            if [ -d ./$cam ] ; then rm -Rf $cam ; fi
            mv -f "UKMON,NEMETODE/$site/$cam" .
        done
    done
    rm -Rf "UKMON,NEMETODE"
fi 
mkdir -p ./stacks
mkdir -p ./jpgs
mkdir -p ./mp4s
cp -f */*.jpg ./jpgs
mv -f ./jpgs/*captured_stack* ./stacks
cp -f */*.mp4 ./mp4s
