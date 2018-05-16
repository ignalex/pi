sudo apt-get install postgresql-9.6 postgis postgresql-plpython3-9.6 postgresql-server-dev-9.6 -y

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

# pandas + plotly
sudo apt-get install python-pandas python3-pandas
sudo pip install plotly cufflinks psycopg2 python-daemon pyicloud speedtest-cli sqlalchemy googletrans weather-api gTTS joblib
sudo pip3 install plotly cufflinks psycopg2 python-daemon pyicloud speedtest-cli sqlalchemy googletrans weather-api gTTS joblib

# issues with pynmea2 installing together.
sudo pip install pynmea2
sudo pip3 install pynmea2

# extra for LIRC
sudo apt-get install lirc python3-lirc python-lirc -y
sudo cp ~/git/pi/data/lircrc /etc/lirc/lircrc
sudo cp ~/git/pi/data/lircd.conf /etc/lirc/lircd.conf