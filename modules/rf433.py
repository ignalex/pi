#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 09:07:04 2019

@author: alexander
"""

# converter pinout
# https://learn.sparkfun.com/tutorials/retired---using-the-logic-level-converter

# PI pinout
# https://learn.sparkfun.com/tutorials/raspberry-gpio/all

# temp and humidity
# https://tutorials-raspberrypi.com/raspberry-pi-measure-humidity-temperature-dht11-dht22/
# https://www.raspberrypi-spy.co.uk/2017/09/dht11-temperature-and-humidity-sensor-raspberry-pi/

from __future__ import print_function
from time import  sleep

RF433 =     18 # pin 18 (board) = GPIO23
DHT11 =     12 # GPIO 18
# LED
RED =       11 # GPIO 17
BLUE =      13 # GPIO 27
GREEN =     15 # GPIO 22


#%% GPIO
import RPi.GPIO as GPIO # if there is error on import not found RPI - need to enable device tree from raspi-config
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.INIT = GPIO.HIGH
#GPIO.ON = GPIO.LOW
#GPIO.OFF = GPIO.HIGH

GPIO.setup(RF433, GPIO.OUT, initial = GPIO.INIT) # works when here

#%% color
previous_color = 'off'
def color(value):
    "pins defined in file pins"
    "color(['yellow',''])"
    global previous_color
    requested = value[0].lower() #syntax /control/color/red
    colors = {'off'    : [0,0,0],   'white' : [1,1,1],
              'red'    : [1,0,0],   'green' : [0,1,0], 'blue' :     [0,0,1],
              'yellow' :[1,1,0],    'cyan'  : [0,1,1], 'magneta' :  [1,0,1]
              }
    pins = {0:RED, 1:BLUE, 2:GREEN}
    try:
        for col, setting in enumerate(colors[requested]):
            GPIO.output(pins[col], int(setting))
        previous_color = requested
        return 'color set to ' + requested
    except Exception as e:
        print (e)
        return str(e)

GPIO.setup((RED,GREEN,BLUE), GPIO.OUT, initial = GPIO.INIT) # works when here


#%%

RF_positions = {} #global > will be updated on 1st request


def rf433(value, td = 150 / 1000000, pos=1):
    """wrapper for _rf433
    [group,what]
    returns [{type:[status::bool, message::str}]
    """
    global RF_positions
    print ('rf warapper: value: ' + str(value))
    com = [1 if value[1] in [1, '1','on','ON','True','true'] else 0][0]
    if value[0] == 'light':
        res = [_rf433([5,com], td, pos) ]
    elif value[0] == 'heater':
        res = [_rf433([12,com], td, pos)]
    elif value[0] == 'coffee':
        res = [_rf433([11,com], td, pos)]
    elif value[0] == 'all':
        res = [_rf433([v,com], td, pos) for v in [5,11,12,21]]
    else:
        res = [_rf433([value[0],com], td, pos)]
    RF_positions[value[0]] = com
#    ret= str(value[0]) +'<br>' + '<br>'.join(res)
    return [RF_positions, res] # updating current state > will be [1/0,'string message']

def _rf433(value, td=150 / 1000000, pos=1):
    """[signal, OnOff]
    : 150 - 300 delay good, pin 14 (D5), 5V """
    print ('_rf433' + str(value), td, pos)
    signal = value[0]
    OnOff  = int(value[1])
    signals= {'1' : [
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,2,4,4,4,2,2,2,2,2,4,4,2,3],
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,4,4,4,4,2,2,2,2,4,2,4,2,3]
                  ],
              '2':  [
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,2,2,4,4,2,2,2,2,2,2,2,4,3],
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,4,2,4,4,2,2,2,2,4,4,4,2,3]
                  ],
              '3':  [
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,2,4,2,4,2,2,2,2,2,4,2,4,3],
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,4,4,2,4,2,2,2,2,4,2,2,4,3]
                  ],
              '4':  [
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,2,4,4,2,2,2,2,2,2,4,4,4,3],
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,4,4,4,2,2,2,2,2,4,2,4,4,3]
                  ],
              # for all 1-4
              '5':  [
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,4,2,2,2,2,2,2,2,4,4,2,2,3],
                  [2,4,2,4,2,2,2,2,4,2,4,2,4,4,2,4,2,2,2,2,2,4,2,2,2,2,2,2,2,4,2,2,3]
                  ],
              '11': [
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,4,4,4,2,2,2,2,2,4,2,4,4,2,3],
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,4,4,4,4,2,2,2,2,4,2,4,2,2,3]
                  ],
              '12': [
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,4,4,2,2,2,2,2,2,4,2,2,4,2,3],
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,4,4,2,4,2,2,2,2,4,2,2,2,2,3]
                  ],
              '13': [
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,4,2,4,2,2,2,2,2,4,4,2,4,2,3],
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,4,2,4,4,2,2,2,2,4,4,2,2,2,3]
                  ],
              '14': [
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,2,4,4,2,2,2,2,2,2,2,4,4,2,3],
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,2,4,4,4,2,2,2,2,2,2,4,2,2,3]
                  ],
              '99': [ # all 4
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,4,2,2,2,2,2,2,2,4,4,4,2,2,3],
                  [4,2,2,4,4,2,4,2,4,4,4,2,2,2,2,2,2,2,2,2,2,4,2,2,2,2,2,2,2,2,2,4,2,3]
                  ],
              # another module > not used.
              '21': [
                  [1,4,1,4,1,4,1,4,1,1,1,1,1,1,1,1,1,1,1,4,4,4,1,1,4,1,1,4,1,1,4,4,4,4,4,1,1,1,1,4,4,4,4,4,4,4,4,6],
                  [1,4,1,4,1,4,1,4,1,1,1,1,1,1,1,1,1,1,1,4,4,4,1,1,4,1,1,4,1,1,4,4,4,4,4,1,1,1,1,4,4,4,4,4,4,4,4,6]
                  ]
              }
    mapping = {1 : (3,3), 2 : (3,7), 3: (3,92), 4: (7,3), 5 : (7,7), 6 : (7,92)}

#    p = Pin(pin , Pin.OUT)
#    GPIO.setup(RF433, GPIO.OUT, initial = GPIO.INIT)

    try:
        for n in range(0,8):
            for i in signals[str(signal)][OnOff]:
#                p.high()
                GPIO.output(RF433, pos)
                #led.high()
                sleep((mapping[i][0] * td))
#                p.low()
                GPIO.output(RF433, int(not pos))
                #led.low()
                sleep((mapping[i][1] * td))
        #led.high()
        sleep(0.2)
        #GPIO.cleanup(RF433) # no cleanup > otherwise jamming 433
        return str('signal {} sent to {}'.format(OnOff,signal))
    except Exception as e:
        print (str(e))
        return str(e)
