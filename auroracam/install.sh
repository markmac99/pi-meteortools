#!/bin/bash
# copyright mark mcintyre, 2024-

sudo apt-get install python3-opencv lighttpd virtualenv
virtualenv ~/vAuroracam  
source ~/vAuroracam/bin/activate  
pip install --upgrade pip
mkdir -p ~/source/auroracam
mkdir -p ~/data/{auroracam,logs}
chmod 755 ~
cd ~/source/auroracam
[ -f config.ini ] && mv config.ini config.bkp
flist=(startAuroraCam.sh archiveData.sh auroraCam.py config.ini setExpo.py sendToYoutube.py makeImageIndex.py imgindex.html.template index.html redoTimelapse.py archAndFree.py mqtt.cfg requirements.txt) 
for f in ${flist[@]} ; do

[ -f ${f} ] && rm ${f}
wget https://raw.githubusercontent.com/markmac99/pi-meteortools/master/auroracam/${f}  
done 
chmod +x *.sh
pip install -r requirements.txt
sudo cp index.html /var/www/html
sudo ln -s $HOME/data /var/www/html
grep dir-listing /etc/lighttpd/lighttpd.conf
if [ $? -eq 1 ] ; then 
sudo chmod 666 /etc/lighttpd/lighttpd.conf 
echo server.dir-listing = \"enable\" >> /etc/lighttpd/lighttpd.conf 
sudo chmod 644 /etc/lighttpd/lighttpd.conf
sudo systemctl restart lighttpd
fi 
