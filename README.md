# Jason
Tor Traffic Router and Ram Wipe tool 

How To Install Jason 

cd jason/DEBIAN 
chmod 755 -R control postinst postrm 

sudo dpkg-deb -b jason/ Jason.deb

sudo dpkg -i Jason.deb
apt-get -f install
