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
"""

import sys, datetime
from modules.weatherzone import WEATHER as WEATHER_class
from time import sleep
from modules.common import   MainException, LOGGER, CONFIGURATION
from modules.PingIPhone import AcquireResult
#import daemon #TODO: >> takes 100% CPU? why? 
from modules.talk import  Speak
from modules.control_esp import ESP

class TIMING(object):
    def __init__(self, stop = 1):
        self.start = datetime.datetime.now()
        self.stop = self.start + datetime.timedelta(hours = stop)
    def CheckTimeToStop(self):
        return [False if datetime.datetime.now() > self.stop else True for i in [1]][0]

class SPEAK_TEMP(object):
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

class ONOFF(object):
    def __init__(self):
        self.status = 'off'
    def OnOff(self,com):
        if com != self.status: # changed
            ESP(['6','rf433','heater',str(com)])
            logger.info ( ' > ' + com)
            self.status = com
            if speak and datetime.datetime.now().hour >= 6:
                Speak("heater " + ['ON' if self.status == 'on' else 'OFF'][0] )
#                Phrase({'TYPE' : 'HEATER_' + ['ON' if self.status == 'on' else 'OFF'][0]})

#def TranslateForHornet(agr):
#    Start(temp = {'min' : 20, 'max' : 21} ,armed_time = 1,check_ping = 0, speak = True )

def Start(temp, armed_time, check_ping):
    global log, logger
    t,w,o = TIMING(armed_time),WEATHER_class(),ONOFF()
    w.TempIn()
    s = SPEAK_TEMP(w.temp_in) # initiating
    logger.debug('starting cycle')
    while t.CheckTimeToStop():
        ping = [AcquireResult() if check_ping else True][0]
        w.TempIn()
        if speak and s.Check(w.temp_in): Speak('temperature reached {} degrees'.format(str(int(w.temp_in)))) #Phrase({'TYPE' : 'HEATER_TEMP', 'TMP' : str(int(w.temp_in))})
        logger.info(str(w.temp_in) + str(['\t ping phone: ' + str(ping) if check_ping else ''][0]))
        if w.temp_in <= temp['min'] and ping: # temp less lower lever and PING
            o.OnOff('on')
        elif  ping == False: # lost contact
            o.OnOff('off')
        elif w.temp_in >= temp['max']: # turning off no matter if phone pinged
            o.OnOff('off')
        sleep(30)
    o.OnOff('off')


if __name__ == '__main__':
    """syntax: python heater.py 19 20 1 1 1 [min max time_armed {ping_iphone = 1 / 0}, {speak 0 / 1}]"""
    if sys.argv[1:] == []:
        args = [19,20,1,1,1]
    else:
        args = [float(i) for i in sys.argv[1:] if not i.startswith('-')]
    temp = {'min' : args[0], 'max' : args[1]}

    logger = LOGGER('heater','INFO', True)
    log = logger.info
    p = CONFIGURATION()

    if len(args)> 2:
        armed_time = args[2]
    else:
        armed_time = 1 # default
    if len(args)> 3:
        check_ping = int(args[3])
    else:
        check_ping = False # default
    if len(args)> 4:
        speak = int(args[4])
    else:
        speak = False # default
    logger.info('\n\n' + str(temp) + ' time: ' + str(armed_time) + '\tping: ' + str(check_ping) + '\tspeak:' + str(speak))
    if speak and datetime.datetime.now().hour >= 6 : Speak('starting monitoring temperature inside') #Phrase({'TYPE' : 'HEATER_START', 'T1' : str(int(temp['min'])), 'T2' : str(int(temp['max'])), 'HH' : str(int(armed_time))})
#    with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
    try:
        Start(temp,armed_time,check_ping)
    except:
        MainException()
    if speak: Speak('I am no longer monitoring temperature inside') #Phrase({'TYPE' : 'HEATER_STOP'})
