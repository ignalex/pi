sudo apt-get install postgresql-9.6 -y

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
sudo apt-get install postgis -y

# create extension postgis; 
