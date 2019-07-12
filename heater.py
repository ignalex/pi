# -*- coding: utf-8 -*-
"""
heater control.
keeping temperature inside within range x ... y deg.
* temp scanned from GPIO
* on/pff command sent to remote power outlet using 433MHz - using esp module

syntax:
  python heater.py 19 20 1 1 1
  params :[min max time_armed {ping_iphone = 1 / 0}, {speak 0 / 1}]

Created on Mon Jun 01 21:18:58 2015
@author: ignalex

#DONE: params to ini BUT from cmd possible to overwrite
#DONE: esp or rf433
#TODO: allow for solar > LOGIC PRIORITY : solar production or room TEMPERATURE
#NO: in this or separate? > no
#DONE: temp OUT integration > if Tout < X
#DONE: integration with 'p' > inside or pass params?

#TODO: speak solar
#TODO: allow for indicators
#TODO: allow for 7segments
#DONE: time constraints / from - to (off for night)
#DONE: re-scan temp every (hour?)
#TODO: on fail - restart?
#DONE: rescan params
"""

import sys, datetime
from time import sleep


from modules.common import   MainException, LOGGER, CONFIGURATION
from modules.weatherzone import WEATHER as WEATHER_class

try:
    from modules.PingIPhone import AcquireResult
except:
    print('no PingIPhone imported')

try:
    from modules.talk import  Speak
except:
    print('no speak imported')

try:
    from modules.control_esp import ESP
except:
    print('no esp imported')

try:
    from modules.rf433 import rf433
except:
    print('no rf433 imported')


class SPEAK_TEMP(object):  #TODO: extend to solar
    def __init__(self,temp):
        self.time_spoken = datetime.datetime.now()
        self.temp_spoken = temp
    def Check(self,temp):
        if temp % 1 < 0.1 and abs(temp - self.temp_spoken) >= 0.5 and (datetime.datetime.now() - self.time_spoken).seconds >= 300 and datetime.datetime.now().hour >= 6:
            self.time_spoken = datetime.datetime.now()
            self.temp_spoken = temp
            return True
        else:
            return False

class HEATER(object):
    def __init__(self, p):
        "config params from p: "
        "heater = target|esp,ip|6,command|heater,run_between_hours|5;23,Tmin|19,Tmax|21,minTout_required|25,speak|YES,speak_between_hours|6;22,pingBT|YES,solar|NO,sec_between_update|30"
        self.conf = p.heater
        self.running = False # status of service
        self.status = 'off'
        self.target = self.conf.target # esp or rf433
#        self.weather_last_scanned = None # > not used
        self.RescanWeather()
        self.speak_temp = SPEAK_TEMP(self.weather.temp_in)
        logger.info(str(self.conf.__dict__))

    def esp(self,com):
        "using ESP contorol"
        ESP([str(self.conf.ip),'rf433',self.conf.command,str(com)])
    def rf433(self,com):
        "using rf433  control"
        rf433([self.conf.command, str(com)])

    def _speak(self):
        "decision to speak or not"
        return self.conf.speak \
            and datetime.datetime.now().hour >= self.conf.speak_between_hours[0]\
            and datetime.datetime.now().hour <= self.conf.speak_between_hours[1]

    def OnOff(self,com):
        "main trigger"
        if com != self.status: # changed
            getattr(self, self.target)(com) # running  either esp or rf433
            logger.info ( ' > ' + com)
            self.status = com
            if self._speak(): Speak("heater " + ['ON' if self.status == 'on' else 'OFF'][0] )

    def Armed(self):
        "decide if hours is sutable for work"
        # start time
        if not self.running  and \
                 self.conf.run_between_hours[0] <= datetime.datetime.now().hour <  self.conf.run_between_hours[1]: # within hours:
            self.running = True
            if self._speak(): Speak('I am starting monitoring temperature inside')
            logger.info('I am starting monitoring temperature inside')

        # stop time
        if self.running  and  \
                not (self.conf.run_between_hours[0] <= datetime.datetime.now().hour <  self.conf.run_between_hours[1]): # outside hours:
            self.running = False
            self.OnOff('off')
            if self._speak(): Speak('I am no longer monitoring temperature inside')
            logger.info('I am no longer monitoring temperature inside')
        return  self.running

    def RescanWeather(self):
        if not hasattr(self,'weather_last_scanned'): # first time
            self.weather = WEATHER_class() #create, using p.weather from default {host}.ini
            self.weather_last_scanned = datetime.datetime.now().hour
        else:
            if self.weather_last_scanned != datetime.datetime.now().hour:
                self.weather_last_scanned = datetime.datetime.now().hour
                self.weather.Update() # once an hour

    def RescanParams(self):
        p = CONFIGURATION()
        if p.heater.__dict__ != self.conf.__dict__ :
            self.conf = p.heater
            if self._speak(): Speak('heater configuration paramaters have been changed')
            logger.info('heater configuration paramaters have been changed')
            logger.info(str(self.conf.__dict__))

    def Start(self):

        logger.info('starting cycle')
        while True: #infinite loop
            ping = AcquireResult() if self.conf.pingBT else True
            self.weather.TempIn() #rescanning temp inside (gpio or esp method) #TODO: extra similar for solar
            if self._speak() and self.speak_temp.Check(self.weather.temp_in):
                Speak('temperature reached {} degrees'.format(str(int(self.weather.temp_in))))

            logger.info(str('armed'  if self.Armed() else 'disarmed') +\
                        '\tTin ' + str(self.weather.temp_in) +\
                        '\ttoday ' + str(self.weather.temp_today) + ', (<= '+ str(self.conf.minTout_required) + ')' + \
                        str('\tBT: ' + str(ping) if self.conf.pingBT else '')
                        )

            if self.weather.temp_in <= self.conf.Tmin and self.weather.temp_today <= self.conf.minTout_required and ping: # temp less lower lever and PING
                if self.Armed():
                    self.OnOff('on')
            elif  ping == False: # lost contact
                #if self.Armed(): # turning off on lost BT contact possible even after hours
                self.OnOff('off')
            elif self.weather.temp_in >= self.conf.Tmax: # turning off no matter if phone pinged
                if self.Armed():
                    self.OnOff('off')
            sleep(self.conf.sec_between_update)

            if self.weather_last_scanned != datetime.datetime.now().hour:
                self.weather_last_scanned = datetime.datetime.now().hour
                self.weather = WEATHER_class() # once an hour #TODO: instead recreating > re-read / mod class
            self.RescanParams()

    def Stop(self): #run at the end of service
        self.OnOff('off')
        if self._speak(): Speak('I am no longer monitoring temperature inside')
        logger.info('STOPPING')

if __name__ == '__main__':

    logger = LOGGER('heater','INFO', True)
    p = CONFIGURATION()

    try:
        heater = HEATER(p)
        heater.Start()
    except:
        heater.Stop()
        MainException()
