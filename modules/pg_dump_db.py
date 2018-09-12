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
#DONE: generic backup + crontab
import sys
import os
import datetime
sys.path.append('/home/pi/git/pi/modules') #compatibility
from common import CONFIGURATION, LOGGER, Dirs
from send_email import sendMail

def dump_db(connection='hornet_pi_db'):
    config = getattr(CONFIGURATION(), connection).__dict__
    config['FILENAME'] = os.path.join(Dirs()['LOG'], connection+'_dmp_' + str(datetime.datetime.now()).split(' ')[0].replace('-',''))
    cmd = "pg_dump -h {HOST} -p {PORT} -d {DB} -U {USER} -s -f {FILENAME}".format(**config)

    logger.info(cmd)
    os.system(cmd)
    logger.info('sending email ... ' + \
                sendMail([p.email.address], \
                         [p.email.address, p.email.login, p.email.password],\
                         'DB backup structure and crontab', \
                         config['FILENAME'], \
                         [config['FILENAME'], os.path.join(Dirs()['LOG'],'crontab')])
                )

def dump_crontab(file='/var/spool/cron/crontabs/pi'):
    cmd = 'sudo cat {} > {}'.format(file, os.path.join(Dirs()['LOG'],'crontab'))
    logger.info(cmd)
    os.system(cmd)


if __name__ == '__main__':
    "syntax: python pd_dump_db hornet_pi_db"
    if len(sys.argv) >1 :
        arg = sys.argv[1]
    else:
        arg = 'hornet_pi_db'
    p = CONFIGURATION()
    logger = LOGGER('dumping db and crontab')
    dump_crontab()
    dump_db(arg)