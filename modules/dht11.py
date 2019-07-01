#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:18:29 2019

# temp and humidity
# https://tutorials-raspberrypi.com/raspberry-pi-measure-humidity-temperature-dht11-dht22/
# https://www.raspberrypi-spy.co.uk/2017/09/dht11-temperature-and-humidity-sensor-raspberry-pi/


@author: alexander
"""
from __future__ import print_function

from time import sleep 
import Adafruit_DHT
from common import CONFIGURATION
p = CONFIGURATION()

#%% temp and humidity
def dht11(correct=(0,0)):
    "returns (temperature, humidity)"
    "correct is (0,0) - for adjusting TEMP and HUMIDITY"
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, p.pins.DHT11)
    while temperature is None:
        sleep (0.05)
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, p.pins.DHT11)
    return (temperature + correct[0], humidity + correct[1])

#%%
if __name__ == '__main__': 
    print (dht11())