#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 07:11:05 2020

@author: alexander
"""

# An Accessory for a MotionSensor
import sys, os
from time import  sleep
sys.path.append('/home/pi/git/pi/modules') #!!!: out
from modules.common import  CONFIGURATION, TIMER, CheckTime, OBJECT

# import datetime
import logging
import requests
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
p = CONFIGURATION() #pins


from modules.PingIPhone import AcquireResult
from modules.talk import  Speak
# from send_email import sendMail

import RPi.GPIO as GPIO

from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR


class MotionSensor(Accessory):

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_motion = self.add_preload_service('MotionSensor')
        self.char_detected = serv_motion.configure_char('MotionDetected')
        self.timer = OBJECT({'morning':      TIMER(60*60*6, [0,1,2,3,4,10,11,12,13,14,15,16,17,18,19,20,21,22,23], 60*7),
                             'CheckTime' :   CheckTime,
                             'last' :        TIMER(60),
                             'report' :      TIMER(60*2, [6])})

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(p.pins.MOVEMENT_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP) #DONE: UP works
        GPIO.setup(p.pins.BLINK, GPIO.OUT, initial = GPIO.LOW)

        GPIO.add_event_detect(p.pins.MOVEMENT_SENSOR, GPIO.RISING, callback=self._detected)

    def _detected(self,_pin):
        if self.timer.last.CheckDelay():
            self.char_detected.set_value(True)
            logger.info('motion')
            self.onMotion()
            sleep(5)
            self.char_detected.set_value(False)

    def stop(self):
        super().stop()
        GPIO.cleanup()

    def Blink(self, args = [1,1,0.1]):
        "cycles, times, onTime / offTime, sleep 0.3 between cycles"
        for b in range(int(args[0])):
            for a in range(int(args[1])):
                GPIO.output(p.pins.BLINK, GPIO.HIGH)
                sleep(float(args[2]))
                GPIO.output(p.pins.BLINK, GPIO.LOW)
                sleep(float(args[2]))
            if int(args[0]) != 1: sleep(0.3)

    def onMotion(self):
        "actions tools"
        if AcquireResult(): # I am home
            self.Blink()
            # morning
            if  self.timer.morning.Awake() and self.timer.morning.CheckDelay():
                logger.info('morning procedure')
                os.system('curl localhost:8083/cmnd?RUN=MORNING')
                # os.system('curl http://192.168.1.176/control/rf433/coffee/on')
                os.system('curl localhost:8083/cmnd?RUN=TIME\&args=HM')
                os.system('curl localhost:8083/cmnd?RUN=TEMP\&args=IN')
                os.system('curl localhost:8083/cmnd?RUN=WEATHER')
                os.system('curl localhost:8083/cmnd?RUN=ALLEVENTSTODAY')
        else:
            # motion but i am not around
            if self.timer.report.CheckDelay() and self.timer.report.Awake():
                logger.info('motion detected and reported')
                try:
                    requests.get('http://192.168.1.40:8000/alert', timeout=1, proxies={'http':None})
                except: pass
                Speak('motion detected and reported')
                self.Blink([10, 3, 0.1])
