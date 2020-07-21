#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 07:11:05 2020

@author: alexander
"""

# An Accessory for a MotionSensor
import sys
from time import  sleep
sys.path.append('/home/pi/git/pi/modules') #!!!: out
from modules.common import  CONFIGURATION

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
p = CONFIGURATION() #pins


import RPi.GPIO as GPIO


from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR


class MotionSensor(Accessory):

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_motion = self.add_preload_service('MotionSensor')
        self.char_detected = serv_motion.configure_char('MotionDetected')
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(7, GPIO.IN)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(p.pins.MOVEMENT_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP) #DONE: UP works
        GPIO.setup(p.pins.BLINK, GPIO.OUT, initial = GPIO.HIGH)

        GPIO.add_event_detect(7, GPIO.RISING, callback=self._detected)

    def _detected(self, _pin):
        self.char_detected.set_value(True)
        logger.info('motion detected')
        self.Blink()


    def stop(self):
        super().stop()
        GPIO.cleanup()

    def Blink(self, args = [1,1,0.1]):
        for b in range(int(args[0])):
            for a in range(int(args[1])):
                GPIO.output(p.pins.BLINK, GPIO.HIGH)
                sleep(float(args[2]))
                GPIO.output(p.pins.BLINK, GPIO.LOW)
                sleep(float(args[2]))
            if int(args[0]) != 1: sleep(0.3)
