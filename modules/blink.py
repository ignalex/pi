# -*- coding: utf-8 -*-
"""
test bliking simple 

Created on Tue Apr 08 12:06:44 2014

@author: aignatov
v1. - triggers basic 
v2. - no start 
"""
import sys
from time import sleep 

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

def blink(pin=18, B=3, N=3, mult=0.1):
    GPIO.setup(pin , GPIO.OUT, initial = GPIO.HIGH)

    for b in range(B):      
        for a in range(N):
            GPIO.output(pin, GPIO.LOW)	
            sleep(mult)
            GPIO.output(pin, GPIO.HIGH)
            sleep(mult)
        sleep(0.3)
    GPIO.cleanup(pin)# - GPIO to be cleaned up in main module only 

#%%
if __name__ == '__main__': 
  
  if len(sys.argv)>1: 
      pin, B, N, mult = int(sys.argv[1]), int(sys.argv[2]),int(sys.argv[3]), float(sys.argv[4])
  else: 
      pin, B, N, mult = 18, 3, 3, 0.1 

  blink(pin, B, N, mult)






