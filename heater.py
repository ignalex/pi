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

#TODO: params to ini BUT from cmd possible to overwrite 
#TODO: esp or rf433
#TODO: allow for solar > LOGIC PRIORITY : solar production or room TEMPERATURE
#NO: in this or separate? > no 
#DONE: temp OUT integration > if Tout < X

#TODO: speak solar
#TODO: allow for indicators 
#TODO: allow for 7segments 
"""

import sys, datetime
from modules.weatherzone import WEATHER as WEATHER_class
from time import sleep
from modules.common import   MainException, LOGGER, CONFIGURATION
from modules.PingIPhone import AcquireResult
#import daemon #TODO: >> takes 100% CPU? why? 
from modules.talk import  Speak

try: 
    from modules.control_esp import ESP
except: 
    print ('no ESP imported')    

try: 
    from modules.rf433 import rf433
except: 
    print ('no rf433 imported')

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
        self.ConnectToHeater() 
    def OnOff(self,com):
        if com != self.status: # changed
            getattr(self, self.target)(com) # running  either esp or rf433 
            logger.info ( ' > ' + com)
            self.status = com
            if speak and datetime.datetime.now().hour >= 6:
                Speak("heater " + ['ON' if self.status == 'on' else 'OFF'][0] )
    def ConnectToHeater(self):  
        "using p for using right heater moudle"
        if hasattr(p,'heater'): 
            self.target = p.heater.control # esp or rf433 
        else: 
            self.target = 'esp' # default BUT should  not be used! (no p defined)
        logger.info('control set to ' + self.target)

    def esp(self,com):  
        "using ESP contorol"
        ESP([str(p.heater.ip),'rf433',p.heater.command,str(com)])
    def rf433(self,com):
        "using rf433  control" 
        rf433([p.heater.command, str(com)])
        
def Start(temp, armed_time, check_ping):
    global log, logger
    t,w,o = TIMING(armed_time),WEATHER_class(),ONOFF()
    # temp_today will be scanned once a day on the start 
    w.TempIn()
    s = SPEAK_TEMP(w.temp_in) # initiating
    logger.debug('starting cycle')
    logger.info('temp_out_required : '+str(temp['t_out_required']) + '\t  temp_out_forecasted' + str(w.temp_today))
    while t.CheckTimeToStop():
        ping = [AcquireResult() if check_ping else True][0] #TODO: extra similar for solar 
        w.TempIn() #DONE: temp or dht11
        if speak and s.Check(w.temp_in): Speak('temperature reached {} degrees'.format(str(int(w.temp_in)))) #Phrase({'TYPE' : 'HEATER_TEMP', 'TMP' : str(int(w.temp_in))})
        logger.info(str(w.temp_in) + str(['\t ping phone: ' + str(ping) if check_ping else ''][0]) )
        if w.temp_in <= temp['min'] and w.temp_today <= temp['t_out_required'] and ping: # temp less lower lever and PING
            o.OnOff('on')
        elif  ping == False: # lost contact
            o.OnOff('off')
        elif w.temp_in >= temp['max']: # turning off no matter if phone pinged
            o.OnOff('off')
        sleep(30)
    o.OnOff('off')


if __name__ == '__main__':
    """syntax: python heater.py 19 20 21 1 1 1 [min max Tout_required time_armed {ping_iphone = 1 / 0}, {speak 0 / 1}]"""
    if sys.argv[1:] == []:
        args = [19,21,22,1,1,1]
    else:
        args = [float(i) for i in sys.argv[1:] if not i.startswith('-')]
    temp = {'min' : args[0], 'max' : args[1], 't_out_required' : args[2]} # t_out injection

    logger = LOGGER('heater','INFO', True)
    log = logger.info
    p = CONFIGURATION()

    if len(args)> 3:
        armed_time = args[3]
    else:
        armed_time = 1 # default
    if len(args)> 4:
        check_ping = int(args[4])
    else:
        check_ping = False # default
    if len(args)> 5:
        speak = int(args[5])
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
