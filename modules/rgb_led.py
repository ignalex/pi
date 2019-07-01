#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:24:53 2019

@author: alexander
"""
from __future__ import print_function
import sys, time 

from common import CONFIGURATION
p = CONFIGURATION()

import RPi.GPIO as GPIO # if there is error on import not found RPI - need to enable device tree from raspi-config
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.INIT = GPIO.HIGH
GPIO.setup((p.pins.RED,p.pins.GREEN,p.pins.BLUE), GPIO.OUT, initial = GPIO.INIT) #TODO: check high 

#%% color
previous_color = 'off' # global 
def color(value):
    "pins defined in file pins"
    "color(['yellow','']) or color('yellow')"
    " color('available') for all options" 
    global previous_color
   
    requested = value.lower() if type(value) == str else value[0].lower()
    
    colors = {'off'    : [0,0,0],   'white' : [1,1,1],
              'red'    : [1,0,0],   'green' : [0,1,0], 'blue' :     [0,0,1],
              'yellow' : [1,1,0],   'cyan'  : [0,1,1], 'magneta' :  [1,0,1]
              }
    if requested == 'available':   # options 
        return colors.keys()
    
    pins = {0 : p.pins.RED, 
            1 : p.pins.BLUE, 
            2 : p.pins.GREEN}
    try:
        for col, setting in enumerate(colors[requested]):
            GPIO.output(pins[col], int(setting))
        previous_color = requested
        return 'color set to ' + requested
    except Exception as e:
        print (e)
        return str(e)

#%%
if __name__ == '__main__': 
  
  if len(sys.argv)>1: 
      color(sys.argv[1])
  else: 
      # test for all  options 
      for c in list(color('available')) + ['off'] : 
          print (color(c))
          time.sleep(1)
