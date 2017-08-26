# -*- coding: utf-8 -*-
"""
basic relay 
"""
from __future__ import print_function

from time import sleep 
import RPi.GPIO as GPIO

class Relay(object): 
    'doesnt work right > on setup it is on, on clean - off'
    def __init__(self, r ):
        self.dict = {1: 23 , 2 : 13 , 3 : 27, 4: 19} # mapping to BCM GPIO
        self.gpio = self.dict[r]
        self.name = r
        GPIO.setmode(GPIO.BCM)
    def ON(self): 
        GPIO.setup(self.gpio, GPIO.OUT)
    def OFF(self): 
        GPIO.cleanup(self.gpio) 

def cascade(rr = [],  delay_between = 0.1, total = 1, off_in_reverse_order = True): 
    "on relays rr for time with delay between delay"
    R = [Relay(r) for r in rr]  # initiate, no triggers 
    for r in R: 
        r.ON(); 
        print (r.name, ' ON')
        sleep(delay_between)
    sleep(total); print ('')
    
    if off_in_reverse_order: R.reverse() # turning off in reverse order 
    for r in R: 
        r.OFF()
        print (r.name, ' OFF',)    
        sleep(delay_between)  
    print  ('')

