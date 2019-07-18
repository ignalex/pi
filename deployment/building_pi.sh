
#headless setup
#https://desertbot.io/blog/headless-raspberry-pi-3-bplus-ssh-wifi-setup

# POSTGRES
sudo apt-get install postgresql postgis postgresql-server-dev-11 #postgresql-9.6 postgresql-plpython3-9.6 postgresql-server-dev-9.6 -y


# sudo su postgres
# createuser pi -P
# pi
# pi

# pslq
# create database pi;
# alter user pi with superuser;
# sudo nano /etc/postgresql/9.6/main/postgresql.conf
# listen_addresses line and change its value from localhost to *

# sudo nano /etc/postgresql/9.6/main/pg_hba.conf
# change 127.0.0.1/32 to 0.0.0.0/0
# change ::1/128 to ::/0
sudo service postgresql restart

# postgis
#sudo apt-get install postgis -y


# create extension postgis;
# create extension plpython3u;

# extra for python
sudo apt-get install python-dev python3-dev ipython ipython3
sudo apt-get install mpg123
sudo apt-get install fbi

#for homeKit
sudo apt-get install libavahi-compat-libdnssd-dev
sudo pip3 install HAP-python[QRCode]

# pandas + plotly
sudo apt-get install python-pandas python3-pandas
sudo pip install plotly cufflinks psycopg2 python-daemon  speedtest-cli sqlalchemy googletrans weather-api gTTS joblib
sudo pip3 install plotly cufflinks psycopg2 python-daemon  speedtest-cli sqlalchemy googletrans weather-api gTTS joblib

#pyicloud
#NEED TO  install from GIT > 
pip3 uninstall pyicloud
pip3 install git+https://github.com/danielfmolnar/pyicloud

# flask server
sudo pip install flask-compress
sudo pip3 install flask-compress

# guni
sudo  apt-get install gunicorn

# issues with pynmea2 installing together.
sudo pip install pynmea2
sudo pip3 install pynmea2

# extra for LIRC
sudo apt-get install lirc python3-lirc python-lirc -y
sudo cp ~/git/pi/data/lircrc /etc/lirc/lircrc
sudo cp ~/git/pi/data/lircd.conf /etc/lirc/lircd.conf

# installying ffmpeg on RPi3
https://github.com/tgogos/rpi_ffmpeg

# transmission
# from here https://linuxconfig.org/how-to-set-up-transmission-daemon-on-a-raspberry-pi-and-control-it-via-web-interface
sudo apt-get update && sudo apt-get install transmission-daemon

# samba share
# from https://www.raspberrypi.org/magpi/samba-file-server/
sudo apt-get install samba samba-common-bin

#SPI LED 7 segments
https://www.raspberrypi-spy.co.uk/2016/03/7-segment-display-modules-and-the-raspberry-pi/
sudo apt-get install libjpeg-dev
sudo pip3 install pillow==4.0.0
git clone https://github.com/rm-hull/max7219.git
cd max7219
sudo python3 setup.py install


# KODI 
sudo apt-get install kodi 
