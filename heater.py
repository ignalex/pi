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
#DONE: allow for solar > LOGIC PRIORITY : solar production or room TEMPERATURE
#NO: in this or separate? > no
#DONE: temp OUT integration > if Tout < X
#DONE: integration with 'p' > inside or pass params?

#TODO: speak solar
#DONE: allow for indicators
#DONE: allow for 7segments
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

try:
    from modules.rgb_led import color
except:
    print('no rgb.led imported')

try: 
    from modules.sevensegments import SevenSegments
except:
    print('no SevenSegments imported')


class SPEAK_TEMP(object):  #TODO: extend to solar
    def __init__(self,temp):
        self.time_spoken = datetime.datetime.now()
        self.temp_spoken = temp
    def Check(self,temp):
        logger.debug('temp speaking conditions: ' + \
                     ' : '.join([str(temp), str(temp % 1 < 0.1), 
                      str(abs(temp - self.temp_spoken) >= 0.5), 
                      str((datetime.datetime.now() - self.time_spoken).seconds >= 300), 
                      str(datetime.datetime.now().hour >= 6)]))
        if temp % 1 < 0.1 and abs(temp - self.temp_spoken) >= 0.5 and (datetime.datetime.now() - self.time_spoken).seconds >= 300 and datetime.datetime.now().hour >= 6:
            self.time_spoken = datetime.datetime.now()
            self.temp_spoken = temp
            return True
        else:
            return False

class HEATER(object):
    def __init__(self, p):
        "config params from p: "
        """heater = target|esp,ip|6,command|heater,run_between_hours|5;23,Tmin|19,Tmax|21,minTout_required|25,speak|YES,speak_between_hours|6;22,
            pingBT|YES,solar|NO,sec_between_update|30,dash|NO,
            segments|NO,
        ... kW_need|123 -  extra for if solar|YES
        colors LED >    red if ON, 
                        blue if OFF. 
                        off if disable 
        """
        self.conf = p.heater
        self.running = False # status of service
        self.status = 'off'
        self.target = self.conf.target # esp or rf433
        self.RescanWeather()
        # in some cases temp still unnavailable on start 
        self.speak_temp = SPEAK_TEMP(self.weather.temp_in if hasattr(self.weather, 'temp_in') else 0)
        if self.conf.dash: 
            self.dash = SevenSegments() #self.segments.seg.text = ...
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
            # report > led 
            if self.conf.led: color('red' if com  == 'on' else 'blue') 
            logger.info ( ' > ' + com)
            self.status = com
            if self._speak(): Speak("heater " + ['ON' if self.status == 'on' else 'OFF'][0] )

    def Armed(self):
        "decide if hours is sutable for work"
        # start time
        if not self.running  and \
                 self.conf.run_between_hours[0] <= datetime.datetime.now().hour <  self.conf.run_between_hours[1]: # within hours:
            self.running = True
            if self.conf.led: color('blue' if self.running else 'off') 
            if self._speak(): Speak('I am starting monitoring temperature inside')
            logger.info('I am starting monitoring temperature inside')
            

        # stop time
        if self.running  and  \
                not (self.conf.run_between_hours[0] <= datetime.datetime.now().hour <  self.conf.run_between_hours[1]): # outside hours:
            self.running = False
            self.OnOff('off')
            if self.conf.led: color('blue' if self.running else 'off') 
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
        if self.conf.dash: self.dash.message('READY',0.5)
        while True: #infinite loop
            ping = AcquireResult() if self.conf.pingBT else True
            self.weather.TempIn() #rescanning temp inside (gpio or esp method) 
            if self.conf.solar: self.weather.Solar()
                
            if self._speak() and self.speak_temp.Check(self.weather.temp_in):
                Speak('temperature reached {} degrees'.format(str(int(self.weather.temp_in))))

            logger.info(str('armed'  if self.Armed() else 'disarmed') +\
                        '\tIN ' + str(self.weather.temp_in) +\
                        '\tOUT ' + str(self.weather.temp_today) + ' (@ '+ str(self.conf.minTout_required) + ')' + \
                        str('\tBT: ' + str(ping) if self.conf.pingBT else '') + \
                        str('\tSLR: ' + str(self.weather.solar if hasattr(self.weather, 'solar') else '' ))
                        )
            if self.conf.dash: #!!!: here need to adjust spaces
                self.dash.seg.text = str(self.weather.temp_in) + ' ' + \
                                     str(self.weather.solar.rjust(5) if hasattr(self.weather, 'solar') else '----' )
                
            # normal > ON
            if self.weather.temp_in <= self.conf.Tmin and self.weather.temp_today <= self.conf.minTout_required \
                and ping \
                and ((self.weather.solar >= self.conf.kW_need) if self.conf.solar else True): # temp less lower lever and PING
                if self.Armed():
                    self.OnOff('on')
                    
            # lost contact
            elif  ping == False: 
                #if self.Armed(): # turning off on lost BT contact possible even after hours
                self.OnOff('off')
                
            # temp inside too hot: (turning off no matter if phone pinged)
            elif self.weather.temp_in >= self.conf.Tmax: # turning off no matter if phone pinged
                if self.Armed():
                    self.OnOff('off')
                    
            #solar doesnt produce enough or lost contact to solar system 
            elif  self.conf.solar \
                and ((self.weather.solar <  self.conf.kW_need) \
                     or self.weather.solar is None): # can't read solar
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
        if self.conf.dash: self.dash.message('DISARMED',0.5)
        if self.conf.led: color('blue' if self.running else 'off') 

if __name__ == '__main__':

    logger = LOGGER('heater','INFO', True)
    p = CONFIGURATION()

    try:
        heater = HEATER(p)
        heater.Start()
    except:
        heater.Stop()
        MainException()
