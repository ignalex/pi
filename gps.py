# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 08:46:42 2018
@author: Alexander Ignatov
GPS comms module

"""
from __future__ import print_function
import os
import serial
import pynmea2
import time, datetime
import psycopg2
from modules.common import  LOGGER, CONFIGURATION, MainException

def PG_Connect(connect):
    """creates cursor on the database
    inputs: dict {DB, USER, HOST, (PORT - optional - if not provided then 5432), (PASS - optional - if not provided to be taken from .pgpass file)}
    output: (conn,cur)"""

    connection =  ("dbname={DB} user={USER} host={HOST} " + \
                  ['password={PASS} ' if 'PASS' in connect.keys() else ' '][0] + \
                  ['port=5432' if 'PORT' not in connect.keys() else 'port={PORT}'][0]).format(**connect)
    try:
        conn = psycopg2.connect(connection)
        conn.autocommit = True
        cur =  conn.cursor()
        return (conn,cur)
    except:
        return (None,None)

def gps(): #TODO: joblib thread > while having other for process
    while True:
        try:
            sentence = serialStream.readline().decode("utf-8")
            if sentence.find('GGA') > 0:
                data = pynmea2.parse(sentence)
                minsec = str(data.timestamp).split(':')[-2:]
                return dict(time=data.timestamp,
                            time_local = str(datetime.datetime.now()).split(':')[0] + ':' + ':'.join(minsec),
                            lat=data.latitude,
                            lon=data.longitude
#                            ,qual=data.gps_qual,
#                            N_st=data.num_sats,
#                            alt=data.altitude,
#                            age=data.age_gps_data,
#                            hord=data.horizontal_dil
                            )
        except Exception as e:
            logger.error('error in gps module : (wrong format?) : ' + str(e))

def wait_for_gps(device,step=2):
    p.DEVICE = os.path.join('/dev/',device)
    while True:
        if os.path.exists(p.DEVICE):
            logger.debug(p.DEVICE + ' found')
            return
        else:
            logger.debug('no device...')
            time.sleep(2)

if __name__ == '__main__':
    logger = LOGGER('gps', level = 'DEBUG')
    logger.info('starting')
    p = CONFIGURATION()

    try:
        time.sleep(int(p.GPS.wait))
        wait_for_gps(p.GPS.device)
        serialStream = serial.Serial(p.DEVICE, 9600, timeout=None)# float(p.GPS.timeout))
        conn, cur = PG_Connect(p.zero1_pi_db.__dict__)
        while True:
            di = gps(); time.sleep(float(p.GPS.sleep))
            print ("{time}: {time_local}: {lat},{lon}".format(**di))# + ' ' + str({k:v for k,v in di.items() if k not in ['time','lat','lon']}))
            if di['lat'] != 0: # no data
                try:
                    cur.execute("insert into readings (stamp, lon, lat) values ('{time_local}' :: timestamp without time zone,{lon},{lat})".format(**di))
                except Exception as e:
                    if str(e).find('Connection timed out') != -1:
                        logger.info('Connection timed out, resetting')
                        conn, cur = PG_Connect(p.zero1_pi_db.__dict__)
            else:
                logger.info('lat lon 0 0')
    except:
        MainException()