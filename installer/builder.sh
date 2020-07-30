#!/bin/bash

curdir=`dirname $0`

if [ "$1" == "" ] ; then
  echo "usage: ./builder.sh {live|arch}"
  exit 1
fi
if [ "$1" == "arch" ] ; then
  PKG=ARCHIVE
else
  PKG=LIVE
fi

cd $curdir/$1
echo "compressing the files"
tar cvfz payload.tgz  * .ukmondec
mv payload.tgz ..
cd $curdir
echo "creating the installer"
cat inst.template |sed "s/THIS/$PKG/;s/CRF/$1/g" > installUkMon$1.sh
cat payload.tgz >> installUkMon$1.sh
chmod 0755 installUkMon$1.sh
rm -f payload.tgz
echo "done"
exit 0

