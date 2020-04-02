# -*- coding: utf-8 -*-
"""
Created on Mon Aug 04 17:32:17 2014

@author: aignatov

- scan iCloud calendar and remind (voice) in ... min before

- ESP integration (total dark trigger)  [DISABLED]
- distance to home trigger              [DISABLED]
- 2FA icloud > integration

#DONE: as service
#DONE: merge PA and PA_service (into pas :) > listen to port XXXX - trigger
#DONE: from CMD: pa {command} will send com to port
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
from modules.talk import Speak, Phrase
#from modules.sunrise import Sun #Astro
from PA import (REMINDER, TIME, TEMP, WEATHER, ESP,  SPENDINGS)

from flask import Flask, request, jsonify

#from tracking import DistanceToPoint
#from modules.sunrise import IsItNowTimeOfTheDay
#from modules.control_esp import ESP #control_esp as ESP >> high CPU usage on JOBLIB - !!!!!!!!! to fix

# disabling warning message
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

import __main__ as m

#%% app
app = Flask(__name__)

@app.route("/cmnd")
def command():
    """get and run command by GET method"
    "/cmnd?RUN={module}&args={args}"
    "args=HR;AA --- etc."
    curl localhost:8083/cmnd?RUN=TIME\&args=HM
    curl localhost:8083/cmnd?RUN=TIME
    curl localhost:8083/cmnd?RUN=TEMP\&args=IN
    curl localhost:8083/cmnd?RUN=WEATHER
    curl localhost:8083/cmnd?RUN=SPENDINGS
    curl localhost:8083/cmnd?RUN=ALLEVENTSTODAY
    curl localhost:8083/cmnd?RUN=MORNING
    """

    global p, m
    RUN, args = request.args.get('RUN'), request.args.get('args')
    m.logger.debug('PARAMS: ' + str(RUN) +  ' : ' + str(args))
    if RUN is None:
        m.logger.error('no module in RUN')
        return jsonify({'status' : 'ERROR', 'message' : 'no module in RUN'})
    if RUN not in globals():
        # trying phrase
        ok,  message = GENERAL([RUN])
        if ok:
            m.logger.info('API RUN : Phrase = {} : OK'.format(str(RUN)))
            return jsonify({'status' : ok, 'message' : 'Phrase = {}'.format(str(RUN)), 'text' : message})
        else:
            m.logger.error('API RUN = {}, module not loaded'.format(str(RUN)))
            return jsonify({'status' : ok, 'message' : 'RUN = {}, module not loaded'.format(str(RUN)), 'text' : message})
    else:
        # module loaded
        args = args.split(';') if args is not None else [] # must be array
        m.logger.info('API RUN : {}, args = {}'.format(RUN,str(args)))
        try:
            resp = globals()[RUN](args)
            return  jsonify({'status' : 'OK', 'message' : resp, 'command' : 'RUN : {}, args = {}'.format(RUN,str(args))})

        except Exception as e:
            m.logger.error(str(e))
            MainException()
            return  jsonify({'status' : 'ERROR', 'message' : str(e)})

def GENERAL(arg):
    try:
        m.logger.debug( str(arg))
        return [True, Phrase({'TYPE' : arg[0]})] # speak phrase if nothing else.
    except Exception as e:
        m.logger.error( str(e) )
        MainException()
        return [False, str(e)]

def App():
    "run app in a thread"
    app.run(debug=False, use_debugger = False, use_reloader = False, port = 8083, host = '127.0.0.1')

def ALLEVENTSTODAY(args):
    "speak all events from the iCloud calendar > called from inside"
    def AllEvents():
        'returns the string of all todays events'
        ev = iCloudCal(p.iCloudApi, datetime.datetime.today())
        m.logger.debug('read from iCloud > \n' + str(ev))
        return ', '.join([(k + ' at ' + ' '.join([str(i) if i != 0 else '' for i in v['localStartDate'][4:6]])) for (k,v) in ev.items() if v['localStartDate'][3] == datetime.date.today().day])

    events = AllEvents()

    if events not in [None,'']:
        return Speak('today planned in your calendar. ' + str(events)) # translating unicode to str > otherwise error

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
    logger.info('starting app')
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

        # # astro
        # A = Astro()
        # n = [k  for k,v in A.items() if datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) == v]
        # if n != []:
        #     Speak('it is {}. time is {} {}'.format(n[0], now.hour, now.minute))
        #     logger.debug('it is {}. time is {} {}'.format(n[0], now.hour, now.minute))

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
