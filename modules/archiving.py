# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 07:01:13 2018

@author: Alexander Ignatov
"""
from __future__ import print_function

"""
dumping and sending email DB structure

pg_dump -h localhost -d pi -U pi -s -f pi_db_structure_dmp
hornet_pi_db = HOST|192.168.1.155,PORT|5432,USER|pi,PASS|--,DB|pi

must:
    chmod 600 pgpass.conf
    echo $PGPASSFILE
        /home/pi/pgpass.conf
"""
#DONE: generic backup + crontab + profiles
import sys
import os
import datetime
import socket
sys.path.append('/home/pi/git/pi/modules') #compatibility
from common import CONFIGURATION, LOGGER, Dirs
from send_email import sendMail


def dump_crontab(file='/var/spool/cron/crontabs/pi'):
    cmd = 'sudo cat {} > {}'.format(file, os.path.join(Dirs()['LOG'],'crontab.txt'))
    logger.info(cmd)
    os.system(cmd)

def dump_db(connection='hornet_pi_db'):
    config = getattr(CONFIGURATION(), connection).__dict__
    config['FILENAME'] = os.path.join(Dirs()['LOG'], connection+'_dmp_' + str(datetime.datetime.now()).split(' ')[0].replace('-','')+'.txt')
    cmd = "pg_dump -h {HOST} -p {PORT} -d {DB} -U {USER} -s -f {FILENAME}".format(**config)
    logger.info(cmd)
    os.system(cmd)

    #check file created
    dmp_check =   'dump file {} - {}'.format(config['FILENAME'],'exists' if os.path.exists(config['FILENAME']) else 'NOT created!')
    logger.info(dmp_check)
    return (config, dmp_check)

def files_to_backup(config):
    files = [i for i in [config['FILENAME'],
                        os.path.join(Dirs()['LOG'],'crontab.txt'),
                        '/home/pi/.bash_aliases',
                        '/home/pi/.bashrc',
                        '/home/pi/.profile',
                        '/home/pi/git/config.ini',
                        '/home/pi/pgpass.conf'] if os.path.exists(i)]
    return files

def send(config, dmp_check):
    logger.info('attaching files:\n' + '\n'.join(files_to_backup(config)))
    logger.info('sending email ... ' + \
                sendMail([p.email.address], \
                         [p.email.address, p.email.login, p.email.password],\
                         'archive from ' + socket.gethostname(), \
                         str(files_to_backup(config)) + '\n' + dmp_check, \
                         files_to_backup(config)))

if __name__ == '__main__':
    "syntax: python archiving.py {hornet_pi_db}"
    if len(sys.argv) >1 :
        arg = sys.argv[1]
    else:
        arg = ''
    p = CONFIGURATION()
    logger = LOGGER('archiving', level = 'INFO'); logger.info('\n')
    dump_crontab()
    if arg != '':
        config, dmp_check = dump_db(arg)
    else:
        config, dmp_check = {'FILENAME' : ''},  ''
    send(config, dmp_check)