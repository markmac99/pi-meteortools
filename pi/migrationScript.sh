# migration of a camera

if [ "$1" == "" ] ; then
    print usage: migrate.sh STATIONID
    exit
fi 

cd ~/source

station=$1
host="${station,,}"

echo "copying SSH keys"
scp $host:~/.ssh/id_rsa ~/.ssh/${station}_id_rsa
scp $host:~/.ssh/id_rsa.pub ~/.ssh/${station}_id_rsa.pub

scp $host:~/.ssh/ukmon ~/.ssh/ukmon_${station}
scp $host:~/.ssh/ukmon.pub ~/.ssh/ukmon_${station}.pub

scp $host:~/.ssh/$host ~/.ssh/tackley_${station}
scp $host:~/.ssh/$host.pub ~/.ssh/tackley_${station}.pub

echo "copying RMS config"
mkdir -p ~/source/Stations/$station
scp $host:source/RMS/.config ~/source/Stations/${station}/
scp $host:source/RMS/mask.bmp ~/source/Stations/${station}/
scp $host:source/RMS/platepar_cmn2010.cal ~/source/Stations/${station}/

echo "updating RMS config"
sed -i "s/data_dir:.*$/data_dir: ~\/RMS_data\/${station}/g" ~/source/Stations/${station}/.config
sed -i "s/\(.*key:\).*/\1 ~\/.ssh\/${station}_id_rsa/g" ~/source/Stations/${station}/.config
sed -i "s/reboot_after_processing:.*$/reboot_after_processing: false/g" ~/source/Stations/${station}/.config
sed -i "s/ukmon-pitools/ukmon-pitools-${station}/g" ~/source/Stations/${station}/.config

echo "copying ukmon tools"
cd ~/source
if [ ! -d ~/source/ukmon-pitools-${station} ] ; then 
    git clone https://github.com/markmac99/ukmon-pitools.git ./ukmon-pitools-${station}
fi 

scp $host:source/ukmon-pitools/ukmon.ini ~/source/ukmon-pitools-${station}/
scp $host:source/ukmon-pitools/extrascript ~/source/ukmon-pitools-${station}/
cd ~/source/ukmon-pitools-${station}
sed -i "s/ukmon/ukmon_${station}/g" ./ukmon.ini
sed -i "s/source\/RMS/source\/Stations\/${station}/g" ./ukmon.ini

cd ~/source
echo "changes made to config files:"
grep $station ~/source/ukmon-pitools-${station}/ukmon.ini
egrep "$station|reboot_after" ~/source/Stations/${station}/.config

echo done