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
import time
from modules.postgres import PG_Connect #TODO: > pool?
from modules.common import  LOGGER, CONFIGURATION, MainException

def gps(): #TODO: joblib thread > while having other for process
    while True:
        sentence = serialStream.readline().decode("utf-8")
        if sentence.find('GGA') > 0:
            try:
                data = pynmea2.parse(sentence)
                return dict(time=data.timestamp,
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
    logger.into('starting')
    p = CONFIGURATION()

    try:
        time.sleep(int(p.GPS['wait']))
        wait_for_gps(p.GPS['device'])
        serialStream = serial.Serial(p.DEVICE, 9600, timeout=float(p.GPS['timeout']))
        conn, cur = PG_Connect(**p.zero1_pi_db)
        while True:
            di = gps()
            print ("{time}: {lat},{lon}".format(**di))# + ' ' + str({k:v for k,v in di.items() if k not in ['time','lat','lon']}))
            cur.execute('insert into readings (lon, lat) values ({lon},{lat})'.format(**di))
    except:
        MainException()