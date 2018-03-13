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

#plpython3u 
#sudo apt-get install postgresql-plpython3-9.6

# create extension postgis; 
# create extension plpython3u; 

# extra for python 
sudo apt-get install python-dev python3-dev ipython ipython3

# pandas + plotly 
sudo apt-get install python-pandas python3-pandas 
sudo pip install plotly cufflinks psycopg2 python-daemon pyicloud pynmea2
sudo pip3 install plotly cufflinks psycopg2 python-daemon pynmea2