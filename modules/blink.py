# -*- coding: utf-8 -*-
"""
Created on Tue Apr 08 12:06:44 2014

@author: aignatov
v1. - triggers basic 
v2. - no start 
"""
import sys
try: 
	sys.path.append('/storage/PY_modules/')
except: 
	pass 

if len(sys.argv)>1: 
    B, N,mult = int(sys.argv[1]), int(sys.argv[2]),  float(sys.argv[3])
else: 
    B, N,mult = 3, 3, 0.1 

from time import sleep 
 
# -------------------------------------------------------------------------    
channel = 18

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)


GPIO.setup(channel , GPIO.OUT, initial = GPIO.HIGH)

for b in range(B):      
    for a in range(N):
        # -------------- START GPIO ------------------- 
        GPIO.output(channel, GPIO.LOW)	
        sleep(mult)
        GPIO.output(channel, GPIO.HIGH)
        sleep(mult)
    sleep(0.3)


GPIO.cleanup(channel)# - GPIO to be cleaned up in main module only 

