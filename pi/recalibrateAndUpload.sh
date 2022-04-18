#!/bin/bash

# recalibrate the last N days of data using a new platepar
from=8
mkdir ~/RMS_data/ArchivedFiles/tmp >/dev/null 2>&1
fldrs=$(find ~/RMS_data/ArchivedFiles/UK* -type d -mtime -$from | sort)
for fldr in $fldrs ; do
	echo $fldr
	cd ~/source/RMS
	cp ~/source/RMS/platepar_cmn2010.cal $fldr
	bn=$(basename $fldr)
	ftpf=$fldr/FTPdetectinfo_$bn.txt
	# recalibrate, then generate reports 
	python -m RMS.Astrometry.ApplyRecalibrate $ftpf
	python -m Utils.CalibrationReport $fldr
	python -m Utils.ShowerAssociation $ftpf
	pushd ~/RMS_data/ArchivedFiles/tmp
	cp ${fldr}_detected.tar.bz2 .
	bunzip2 ${bn}_detected.tar.bz2
	# copy all the new files to a temp location
	cp -p $fldr/platepar_cmn2010.cal .
	cp -p $fldr/FTPdetectinfo* .
	cp -p $fldr/*.csv .
	cp -p $fldr/${bn}_calibration_variation* .
	cp -p $fldr/${bn}_photometry_variation* .
	cp -p $fldr/${bn}_calib_report* .
	cp -p $fldr/${bn}_radiants* .
	cp -p $fldr/platepars_all_recalibrated.json .

	tar -rf ${bn}_detected.tar ./*.txt ./platepar* ./*.csv ./$bn*.png ./$bn*.jpg
	bzip2 ${bn}_detected.tar
	mv ${bn}_detected.tar.bz2 ..
	rm ./*.txt ./platepar* ./*.csv ./$bn*.png ./$bn*.jpg
	echo ${fldr}_detected.tar.bz2 >> ~/RMS_data/FILES_TO_UPLOAD.inf
	popd
	python ~/source/ukmon-pitools/uploadToArchive.py $fldr
done 
