# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 08:46:42 2018

@author: Alexander Ignatov
"""
from __future__ import print_function

import serial
import pynmea2
from time import sleep

serialStream = serial.Serial("/dev/ttyUSB1", 9600, timeout=0.5)

def gps():
    while True: 
        sentence = serialStream.readline()
        if sentence.find('GGA') > 0:
            try: 
	    	data = pynmea2.parse(sentence)
            	return dict(time=data.timestamp,lat=data.latitude,lon=data.longitude)
	    except: 
		print('wrong format') 

if __name__ == '__main__':
    while True:
        print ("{time}: {lat},{lon}".format(**gps()))
#        sleep(0.5)
