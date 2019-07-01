#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:15:31 2019

SPI
 https://www.raspberrypi-spy.co.uk/2016/03/7-segment-display-modules-and-the-raspberry-pi/
 sudo apt-get install libjpeg-dev
 sudo pip3 install pillow==4.0.0
 from max7219 sudo python3 setup.py install

@author: alexander
"""
import time, sys
from datetime import datetime

import max7219.led as led

class sevensegments(object): 
    def __init__ (self, deviceId=0 ): 
        self.device = led.sevensegment()
        self.deviceId = deviceId
        
    def date(self): 
        now   = datetime.now()
        day   = now.day
        month = now.month
        year  = now.year - 2000
    
        mapping = [year % 10, 
                   int(year / 10), 
                   '-', 
                   month % 10, 
                   int(month / 10),  
                   '-', 
                   day % 10, 
                   int(day / 10)
                   ]
        for n, m in enumerate(mapping): 
            self.device.letter(self.deviceId, n + 1, m)
        
    def writeNumber(self, num): 
        self.device.write_number(deviceId=self.deviceId, value=num, zeroPad=True)
        
    def brightness(self, intensity=16):
        self.device.brightness(intensity)

    def scrollRight(self): 
        # Scroll Text
        for i in range(8):
            self.device.scroll_right()
            time.sleep(0.1)
        
    def clear(self): 
        self.device.clear()
        
if __name__ == '__main__': 
    
    if len(sys.argv)>1: 
        ss = sevensegments(0)
        ss.writeNumber(sys.argv[1])
    else: 
        ss = sevensegments(0)
        ss.date()



