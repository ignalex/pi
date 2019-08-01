# -*- coding: utf-8 -*-
"""
Created on Mon Aug 04 17:32:17 2014

@author: aignatov

- scan iCloud calendar and remind (voice) in ... min before

- ESP integration (total dark trigger)  [DISABLED]
- distance to home trigger              [DISABLED]
- 2FA icloud > integration

#DONE: as service
#TODO: merge PA and PA_service (into pas :) > listen to port XXXX - trigger
#TODO: from CMD: pa {command} will send com to port
#NO: merge with internet_speed + rename to server? > that one is for non iCloud related
#NO: make iCloud OPTIONAL for run > this one core is iCloud
"""

from __future__ import print_function

#import  os
import datetime
from time import sleep
import threading

from modules.common import  LOGGER, PID, CONFIGURATION, MainException#, Dirs
from modules.iCloud import  (iCloudConnect, iCloudCal, re_authenticate, get_Photos)
from PA import REMINDER, TIME

from flask import Flask, request

#from tracking import DistanceToPoint
#from modules.sunrise import IsItNowTimeOfTheDay
#from modules.control_esp import ESP #control_esp as ESP >> high CPU usage on JOBLIB - !!!!!!!!! to fix

# disabling warning message
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

import __main__ as m

#%% app
app = Flask(__name__) #!!!: need to run it in a thread?

@app.route("/cmnd")
def command():
    "get and run command by GET method"
    "/cmnd?RUN={module}&args={args}"
    "args=HR;AA --- etc."
    global p, m
    RUN, args = request.args.get('RUN'), request.args.get('args')
    if RUN is None:
        m.logger.error('no module in RUN')
        return
    if RUN not in globals():
        m.logger.error('RUN = {}, module not loaded'.format(str(RUN)))
        return
    else:
        # module loaded
        args = args.split(';') if args is not None else None # must be array
        m.logger.info('RUN : {}, args = {}'.format(RUN,str(args)))
        try:
            globals()[RUN](args)
        except Exception as e:
            m.logger.error(str(e))

def App():
    "run app in a thread"
    app.run(debug=True, use_debugger = True, use_reloader = True, port = 8083, host = '127.0.0.1')



#%%
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
            localStartDateTime = datetime.datetime(details['localStartDate'][1],details['localStartDate'][2],details['localStartDate'][3],details['localStartDate'][4],details['localStartDate'][5])
            self.times.append(localStartDateTime)
            self.starts[localStartDateTime] = name
            for delta in [float(i)/60 for i in p.REMINDERS.split(',')]:
                self.reminders[localStartDateTime - datetime.timedelta(hours = delta)] = name

def PA_service():
    logger.info('PA service started')
    #esp = ESP()
    p.iCloudApi = iCloudConnect() # keeping connected API for later

    EV = Events(iCloudCal(p.iCloudApi, datetime.datetime.today()))
    logger.info('following events found for today: ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
    logger.info('reminders at ' + ', '.join([str(v).split(' ')[1].split('.')[0] for v in sorted(EV.reminders.keys())]))

    get_Photos(p.iCloudApi)

    p.last_scan = datetime.datetime.now()

    # start listining App port
    threading.Thread(target=App).start()

    while True:
        now = datetime.datetime.now()
        if now - datetime.timedelta(minutes = 5) > p.last_scan:

            #rescan calendar
            logger.info('re-scanning events >> ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
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

            #rescan photos
            logger.debug('rescanning Photo Library')
            #TODO: mount smb
            try:
                get_Photos(p.iCloudApi) # rest args default
            except Exception as e:
                logger.error(str(e))
                MainException()

            p.last_scan = now


        if datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) in EV.reminders.keys(): # and DistanceToPoint(p.iCloudApi, 'HOME') <=200:
            next_event = [v for k,v in EV.reminders.items() if k == datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)][0]
            min_left = int(([k for k, v in EV.starts.items() if v == next_event][0] - now).seconds/60) +1
            reminder = 'reminder_'+ next_event.replace(' ','-') +'_'+str(min_left)
            logger.info(reminder)
            REMINDER(reminder.replace('reminder_','').split('_')) # for backwards compatibility #!!! remove later
        sleep(60)

def pa_reAuth():
    while True:
        try:
            #import daemon
            #with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
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


if __name__ == '__main__':
    logger = LOGGER('pa_service', level = 'INFO')
    p = CONFIGURATION()
    p.last_scan = '' # addition
    PID()

    try:
        pa_reAuth()
    except:
        MainException()
