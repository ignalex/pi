
#headless setup
#https://desertbot.io/blog/headless-raspberry-pi-3-bplus-ssh-wifi-setup

# POSTGRES
sudo apt-get install postgresql postgis postgresql-server-dev-11 postgresql-plpython3-11 #postgresql-9.6 postgresql-plpython3-9.6 postgresql-server-dev-9.6 -y


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

#ssl error
sudo apt-get install rng-tools

#for homeKit
sudo apt-get install libavahi-compat-libdnssd-dev
sudo pip3 install HAP-python[QRCode]

# pandas + plotly
sudo apt-get install python-pandas python3-pandas
sudo pip install plotly cufflinks psycopg2 python-daemon  speedtest-cli sqlalchemy googletrans weather-api gTTS joblib
sudo pip3 install plotly cufflinks psycopg2 python-daemon  speedtest-cli sqlalchemy googletrans weather-api gTTS joblib pybluez

#pyicloud
#NEED TO  install from GIT >
sudo  pip3 uninstall pyicloud
sudo  pip3 install git+https://github.com/danielfmolnar/pyicloud

# flask server
sudo pip install flask-compress
sudo pip3 install flask-compress

# guni
sudo  apt-get install gunicorn3 gunicorn

# issues with pynmea2 installing together.
sudo pip install pynmea2
sudo pip3 install pynmea2

# astral > wont work on py < 3.6
pip install astral
pip3 install astral

#  istall new python
URL https://installvirtual.com/install-python-3-7-on-raspberry-pi/


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

sudo nano /etc/samba/smb.conf
sudo /etc/init.d/samba restart


#SPI LED 7 segments
https://www.raspberrypi-spy.co.uk/2016/03/7-segment-display-modules-and-the-raspberry-pi/
sudo apt-get install libjpeg-dev
sudo pip3 install pillow==4.0.0
git clone https://github.com/rm-hull/max7219.git
cd max7219
sudo python3 setup.py install


# KODI
sudo apt-get install kodi

# mounting samba
sudo mount -t cifs //shrimp.local/ssd_shrimp/ /mnt/shrimp_ssd/ -o vers=1.0,username=pi,password=impervious

# MQTT
sudo apt-get install mosquitto


--- mounting external drive on PI
From
https://www.raspberrypi.org/documentation/configuration/external-storage.md

pi@shrimp:~ $ sudo lsblk -o UUID,NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL,MODEL
UUID                                 NAME        FSTYPE   SIZE MOUNTPOINT   LABEL       MODEL
                                     sda                119.2G                          Tech
A777-7A74                            └─sda1      vfat   119.2G /media/ssd   ssd_zorab
                                     sdb                  1.8T                          HD710
18E9-142B                            └─sdb1      vfat     1.8T /media/adata ADATA HD710

sudo blkid

/dev/sda1: LABEL="ssd_zorab" UUID="A777-7A74" TYPE="vfat" PARTUUID="36c68d8d-01"
/dev/sdb1: LABEL="ADATA HD710" UUID="18E9-142B" TYPE="vfat" PARTUUID="79a8564b-01"

sudo nano /etc/fstab

** for  exfat on linux   : sudo apt-get install exfat-fuse exfat-utils

Works:
# was ok : @reboot sleep 3 && sudo mount -o umask=000 /dev/sda1 /media/ssd
#ADATA
UUID=18E9-142B /media/adata vfat defaults,auto,users,rw,nofail,umask=000,x-systemd.device-timeout=30 0 0
#SSD
UUID=A777-7A74 /media/ssd vfat defaults,auto,users,rw,nofail,umask=000,x-systemd.device-timeout=30 0 0
#IntelSSD - Gecko
UUID=5E4A-343B /media/ssd exfat defaults,auto,umask=000,users,rw 0 0
#SSD-shrimp (ext4)
# >> doesnt work UUID=655c6afe-78ad-4bca-b673-500c85ad7c36 /media/ssd ext4 defaults,auto,users,rw,nofail,umask=000,x-systemd.device-timeout=30 0 0
# works (but careful with ports sda1)
/dev/sda1      /media/ssd   ext4   defaults   0   0

# if screwd fstab > https://www.clarkle.com/notes/emergecy-mode-bad-fstab/ 
# !!! use NON apple keyboard 

# hotspot / access point
# https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

sudo apt install hostapd bridge-utils
sudo systemctl stop hostapd
...  more
** didnt work well on shrimp


# DOCKER
# URL https://pimylifeup.com/raspberry-pi-docker/
# https://medium.com/@mattvonrohr/installing-docker-on-raspberry-pi-4-buster-afde6b0af42
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi
logout
groups
docker run hello-world

# JACKET
docker pull linuxserver/jackett

#docker postgis ??? DOESNT WORK
docker run --name postgis-12-3.0 -e POSTGRES_PASSWORD=impervious -d postgis/postgis
docker run -it --link postgis-12-3.0:postgres --rm postgres sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'
