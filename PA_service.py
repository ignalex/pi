# -*- coding: utf-8 -*-
"""
Created on Mon Aug 04 17:32:17 2014

@author: aignatov
"""
#TODO: list functionality 
from __future__ import print_function

import sys, os, datetime
from time import sleep 
try: 
    sys.path.append( [i for i in ['/home/pi/PYTHON/GPIO/','/home/pi/git/pi/','C:\\Users\\aignatov\\Dropbox\\PI\\GPIO', 'E:\Dropbox\PI'] if os.path.exists(i) == True][0]) 
except: 
    print ('NO SELF PATH CONFIGURED')
    sys.exit()
#TODO: change SHELL TO CONFIG > + move file structure 
from modules.SHELL import LOGGER, PID, PARAMETERS,MainException

#self_path = loging.self_path    
#from modules.iCloud import (iCloudLocation, iCloudConnect, InstantLocation,iCloudCal)
from modules.iCloud import  (iCloudConnect ,iCloudCal)
#TODO: migrate iCloud service 

#from tracking import DistanceToPoint

from modules.sunrise import IsItNowTimeOfTheDay
from modules.control_esp import ESP #control_esp as ESP >> high CPU usage on JOBLIB - !!!!!!!!! to fix 

# disabling warning message 
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

#
#class PARAMETERS (object): 
#    def __init__(self, ID = ''):
#        self.last_scan = ''
#        self.INI = SimpleIni('PA.INI')
#        for p in ['DAEMON', 'SIMULATE','DEBUG']: setattr(self, p, [True if i == 'YES' else False for i in [self.INI[p]]][0])

class Events(object):
    def __init__(self,Events):
        self.reminders = {}
        self.starts = {}
        self.events = {}
        self.names = []
        self.times = []
        self.AddReminders(Events)
       # self.all_events = ', '.join([(v + ' at ' + str(k.hour) + ' ' + str(k.minute)) for (k,v) in self.starts.items()])
    def AddReminders(self, Events): 
        for name,details in Events.items(): 
            self.events[name] = details 
            self.names.append(name)
            startDateTime = datetime.datetime(details['startDate'][1],details['startDate'][2],details['startDate'][3],details['startDate'][4],details['startDate'][5])
            self.times.append(startDateTime)
            self.starts[startDateTime] = name
            for delta in [float(i) for i in params.INI['REMINDERS'].split(',')]:
                self.reminders[startDateTime - datetime.timedelta(hours = delta)] = name
        


def PA_service(): 
    log('PA service started')
    esp = ESP()
    params.iCloudApi = iCloudConnect()
    EV = Events(iCloudCal(params.iCloudApi, datetime.datetime.today())) 
    log('following events found for today: ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
    log('reminders at ' + ', '.join([str(v).split(' ')[1].split('.')[0] for v in sorted(EV.reminders.keys())]))
    params.last_scan = datetime.datetime.now()
    while True: 
        now = datetime.datetime.now()
        if now - datetime.timedelta(minutes = 10) > params.last_scan: 
            log('re-scanning >> ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
            try: 
                EV = Events(iCloudCal(params.iCloudApi,datetime.datetime.today())) 
            except: 
                logger.error('error in iCloud - re-connecting...,')
                try: 
                    params.iCloudApi = iCloudConnect()
                    log(' - DONE. Checking EV...,')
                    EV = Events(iCloudCal(params.iCloudApi,datetime.datetime.today())) 
                    log(' - DONE')
                except: 
                    logger.error(' all bad :( skipping till next update')
                    sleep (60)
                    continue 
            params.last_scan = now
        if datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) in EV.reminders.keys(): # and DistanceToPoint(params.iCloudApi, 'HOME') <=200: 
            next_event = [v for k,v in EV.reminders.items() if k == datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)][0]
            min_left = int(([k for k, v in EV.starts.items() if v == next_event][0] - now).seconds/60) +1
            reminder = 'reminder_'+ next_event.replace(' ','-') +'_'+str(min_left)
            log(reminder)
            os.system('sudo python /home/pi/PYTHON/GPIO/PA.py ' + reminder)
        
        # daytime / esp 
#        if IsItNowTimeOfTheDay('window_light') : esp.Go(['0','1'])
#        if IsItNowTimeOfTheDay('sun_has_gone') : esp.Go(['1','1'])
        if IsItNowTimeOfTheDay('total_dark')   : esp.Go(['0','123'])    

        esp.Decide_On_Off(thresholds = {'count' : 3, 'up' : 350,'down' : 300} )
            
        sleep(60)

if __name__ == '__main__': 
    #loging = LOGGING('PA_service')
    logger = LOGGER('PA_service', 'INFO',True)
    log = logger.info
    PID()
    params = PARAMETERS('PA.INI')
    params.last_scan = '' # addition 
    try: 
        if params.DAEMON == True: 
            import daemon
            with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
                PA_service() 
        else: 
            PA_service()
    except: 
        MainException()