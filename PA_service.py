# -*- coding: utf-8 -*-
"""
Created on Mon Aug 04 17:32:17 2014

@author: aignatov

- scan iCloud calendar and remind (voice) in ... min before

- ESP integration (total dark trigger)  [DISABLED]
- distance to home trigger              [DISABLED]
- 2FA icloud > integration
"""

from __future__ import print_function

#import  os
import datetime
from time import sleep

from modules.common import  LOGGER, PID, CONFIGURATION, MainException#, Dirs
from modules.iCloud import  (iCloudConnect, iCloudCal, re_authenticate)
from PA import REMINDER

#from tracking import DistanceToPoint
#from modules.sunrise import IsItNowTimeOfTheDay
#from modules.control_esp import ESP #control_esp as ESP >> high CPU usage on JOBLIB - !!!!!!!!! to fix

# disabling warning message
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class Events(object):
    def __init__(self,Events):
        self.reminders = {}
        self.starts = {}
        self.events = {}
        self.names = []
        self.times = []
        self.AddReminders(Events)
    def AddReminders(self, Events):
        for name,details in Events.items():
            self.events[name] = details
            self.names.append(name)
            startDateTime = datetime.datetime(details['startDate'][1],details['startDate'][2],details['startDate'][3],details['startDate'][4],details['startDate'][5])
            self.times.append(startDateTime)
            self.starts[startDateTime] = name
            for delta in [float(i)/60 for i in p.REMINDERS.split(',')]:
                self.reminders[startDateTime - datetime.timedelta(hours = delta)] = name

def PA_service():
    logger.info('PA service started')
    #esp = ESP()
    p.iCloudApi = iCloudConnect() # keeping connected API for later
    EV = Events(iCloudCal(p.iCloudApi, datetime.datetime.today()))
    logger.info('following events found for today: ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
    logger.info('reminders at ' + ', '.join([str(v).split(' ')[1].split('.')[0] for v in sorted(EV.reminders.keys())]))
    p.last_scan = datetime.datetime.now()
    while True:
        now = datetime.datetime.now()
        if now - datetime.timedelta(minutes = 10) > p.last_scan:
            logger.info('re-scanning >> ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
            try:
                EV = Events(iCloudCal(p.iCloudApi,datetime.datetime.today()))
            except:
                logger.error('error in iCloud - re-connecting...,')
                try:
                    p.iCloudApi = iCloudConnect()
                    logger.info(' - DONE. Checking EV...,')
                    EV = Events(iCloudCal(p.iCloudApi,datetime.datetime.today()))
                    logger.info(' - DONE')
                except:
                    logger.error(' all bad :( skipping till next update')
                    sleep (60)
                    continue
            p.last_scan = now
        if datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) in EV.reminders.keys(): # and DistanceToPoint(p.iCloudApi, 'HOME') <=200:
            next_event = [v for k,v in EV.reminders.items() if k == datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)][0]
            min_left = int(([k for k, v in EV.starts.items() if v == next_event][0] - now).seconds/60) +1
            reminder = 'reminder_'+ next_event.replace(' ','-') +'_'+str(min_left)
            logger.info(reminder)
#            os.system('python {} {}'.format(os.path.join(Dirs()['REPO'],'PA.py'), reminder))  #TODO: fix > why not via internal call to PA?
            REMINDER(reminder.replace('reminder_','').split('_')) # for backwards compatibility #!!! remove later
        sleep(60)

if __name__ == '__main__':
    logger = LOGGER('pa_service', level = 'INFO')
    p = CONFIGURATION()
    p.last_scan = '' # addition
    PID()

    while True:
        try:
    #        import daemon
    #        with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
            PA_service()
        except:
            error = str(MainException()) # in case nothing returned
            if error.find('Unauthorized') != -1 or error.find('PyiCloudAPIResponseError') != -1:
                while True:
                    if re_authenticate(p.iCloudApi): break # passing existing api / not authenticated
                    sleep(30) # time between attempts
            else:
                logger.info('waiting 1 min and retrying...')
                sleep (60)
