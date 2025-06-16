# Jason
Tor Traffic Router and Ram Wipe tool 

How To Install Jason 

cd jason/DEBIAN 

sudo chmod 755 -R control postinst postrm 



sudo dpkg-deb -b jason/ Jason.deb


sudo apt-get -f install

sudo dpkg -i Jason.deb


