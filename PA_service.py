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
#DONE: sunrise / sunset
#TODO: iPhone status > breaking
#NO: from MS > task 'good morning' : coffee, lights, ...
#DONE: LED colors? ESP(['6', 'color',  ['green' if i else 'red' for i in [iPhone.changed]][0]],'0')
#DONE: light change at night
#DONE: speaking on sunset / sunrise etc

"""

from __future__ import print_function

import  os
import datetime
from time import sleep
import threading

from modules.common import  LOGGER, CONFIGURATION, MainException, OBJECT, TIMER, CheckTime
from modules.iCloud import  (iCloudConnect, iCloudCal, re_authenticate, get_Photos)
from modules.talk import Speak, Phrase
#from modules.sunrise import Sun #Astro
from PA import REMINDER #(REMINDER, TIME, TEMP, WEATHER, ESP,  SPENDINGS)
from modules.PingIPhone import PING
from modules.sunrise import Twilight
from modules.weatherzone import WEATHER as WEATHER_class

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
    curl localhost:8083/cmnd?RUN=ESP\&args="6;color;green"
    curl localhost:8083/cmnd?RUN=ESP\&args="6;rf433;light;off"
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
    app.run(debug=False, use_debugger = False, use_reloader = False, port = 8083, host = '0.0.0.0')

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

def WEATHER(arg):
    w = WEATHER_class()
    w.ToInt()
    m.logger.debug('weather read and parsed ' +  '\t'.join([str(w.temp_out) , str(w.humidity) ,  str(w.pressure) , str(w.rain) , str(w.forecast) , str(w.temp_today)]))
    if w.rain_at_all:
        return Phrase({'TYPE' : 'WEATHER1', 'TEMP' : str(w.temp_out),'HUM' : str(w.humidity), 'PR' : str(w.pressure), \
                'RAIN' : str(w.rain), 'FORECAST': str(w.forecast),'TMAX' : str(w.temp_today), \
                'WIND' : str(w.wind), 'WND_GUST' : str(w.wind_gust)})
    else:
        return Phrase({'TYPE' : 'WEATHER2', 'TEMP' : str(w.temp_out),'HUM' : str(w.humidity), 'PR' : str(w.pressure), \
                'FORECAST': str(w.forecast),'TMAX' : str(w.temp_today), 'WIND' : str(w.wind), 'WND_GUST' : str(w.wind_gust)  })
def TEMP(arg):
    if arg ==  []: arg = ['ALL']
    w = WEATHER_class()
    w.ToInt()
    Phrase({'TYPE' : 'INSIDE_TEMP', 'T' : str(w.temp_in)})
    if arg[0] != 'IN':
        sleep(1)
        return Phrase({'TYPE' : 'OUTSIDE', 'T' : str(w.temp_out),'HUM' : str(w.humidity) })

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
    global timer
    logger.info('PA service started')
    Speak('starting P.A. service')

    #esp = ESP()
    if p.icloud.do: 
        p.iCloudApi = iCloudConnect() # keeping connected API for later
    
        EV = Events(iCloudCal(p.iCloudApi, datetime.datetime.today()))
        logger.info('following events found for today: ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
        logger.info('reminders at ' + ', '.join([str(v).split(' ')[1].split('.')[0] for v in sorted(EV.reminders.keys())]))
    else: 
        logger.info('no iCloud integration') 
        
    p.last_scan = datetime.datetime.now()
    p.last_reminder = datetime.datetime.now()

    # start listining App port
    logger.info('starting app')
    threading.Thread(target=App).start()


    logger.info('starting pinging iPhone')

    iPhone = PING(4,15) # 4 attempts with 15 sec gap
    items = OBJECT({'lamp': OBJECT({'status':False}),
                    'iPhone':OBJECT({'status':iPhone.Status()})})

    TW = Twilight()
    os.system('curl http://192.168.1.176/control/color/yellow')

    ping_pause_time = 5 # starting

    while True:
        now = datetime.datetime.now()

        # rereading SUN times
        if timer.CheckTime(0,0):
            if timer.Sun.CheckDelay():
                TW.today()
                logger.info('Sun times reset : {}'.format(str(TW.twilight_times)))
                os.system('curl http://192.168.1.176/control/color/off')

        # calendar
        if p.icloud.do:
            if timer.iCloud_cal.CheckDelay():            
                #rescan calendar
                try:
                    EV = Events(iCloudCal(p.iCloudApi,datetime.datetime.today()))
                    logger.info('re-scanning events >> ' + ', '.join(EV.names) + ' at ' + ', '.join([str(i).split(' ')[1] for i in EV.times]))
                    logger.info('reminders at ' + ', '.join([str(v).split(' ')[1].split('.')[0] for v in sorted(EV.reminders.keys())]))
                except Exception as e:
                    logger.error(str(e))
                    # ERROR - Service Unavailable (503)
                    # ERROR - statusCode = Throttled, unknown error, http status code = 520
                    if str(e).find('503') != -1 or str(e).find('520') != -1 : 
                        logger.error('Throttling / service not available > holding for 1 h')
                        timer.iCloud_cal.last_scan   = datetime.datetime.now() + datetime.timedelta(minutes=60)
                        timer.iCloud_photo.last_scan = datetime.datetime.now() + datetime.timedelta(minutes=60)
                        continue
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
        if p.icloud_photo.do:
            if timer.iCloud_photo.CheckDelay():
                try:
                    logger.debug('rescanning Photo Library')
                    get_Photos(p.iCloudApi) # rest args default
                except Exception as e:
                    logger.error(str(e))
                    Speak("There is error with syncronizing photographs.  I am trying to remounting the drive")
                    MainException()
                    os.system("sudo mount -t cifs //shrimp.local/ssd_shrimp/ /mnt/shrimp_ssd/ -o username=guest,password=guest,vers=1.0,sec=ntlm")
                    try:
                        get_Photos(p.iCloudApi) # rest args default
                        Speak("looks like remounting drive worked.")
                    except:
                        Speak("no luck. check yourself, Alex")

        if p.icloud.do: 
            if timer.reminders.Awake():
                if timer.reminders.CheckDelay() : # don't repereat witin 1 min and dont speak at night
                    if datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) in EV.reminders.keys(): # and DistanceToPoint(p.iCloudApi, 'HOME') <=200:
                        next_event = [v for k,v in EV.reminders.items() if k == datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)][0]
                        min_left = int(([k for k, v in EV.starts.items() if v == next_event][0] - now).seconds/60) +1
                        reminder = 'reminder_'+ next_event.replace(' ','-') +'_'+str(min_left)
                        logger.info(reminder)
                        REMINDER(reminder.replace('reminder_','').split('_')) # for backwards compatibility #!!! remove later

        if timer.iPhone.Awake():
            if timer.iPhone.CheckDelay(ping_pause_time):
                ping_pause_time = iPhonePING(TW, items, iPhone)

        sleep(5) # increments
        logger.debug(str(now))

def pa_reAuth():
    global p
    while True:
        try:
            PA_service()
        except:
            error = str(MainException()) # in case nothing returned
            if True in [error.find(i) != -1 for i in ['PyiCloud2SARequiredError', 'PyiCloudAPIResponseError', 'Unauthorized']]:
                while True:
                    p.iCloudApi = iCloudConnect()
                    if re_authenticate(p.iCloudApi): break # passing existing api / not authenticated
                    sleep(30) # time between attempts
            else:
                logger.info('waiting 1 min and retrying...')
                Speak('error in P. A. service')
                sleep (60)

#%% iPhone
def iPhonePING(TW, items, iPhone, twilight=True, iPhoneStatus=True):
    global timer

    iPhone.Ping()

    # changed
    if iPhoneStatus:

        if CheckTime(5,0):
            if timer.speak.CheckDelay():
                sleep(0.1); os.system('curl http://192.168.1.176/control/color/' +('green' if iPhone.Status() else 'red'))
                #Speak('Good morning')

        if iPhone.changed != None:
            # os.system('curl http://192.168.1.176/control/color/' +('green' if iPhone.changed else 'red'))  # doesnt work here

            logger.info('iPhone status changed to ' + str(iPhone.changed))

            # WAS ON >> OFF
            if items.iPhone.status: # was on
                if  iPhone.Status() == False: #  changed to OFF
                    iPhone_connection(False)
                    #lamps off on connection lost
                    if items.lamp.status:
                        # ESP(['6','rf433','light','off'])
                        if timer.lamp.CheckDelay():
                            sleep(0.1); os.system('curl http://192.168.1.176/control/rf433/light/off')
                            items.lamp.status = False
                            Speak('lights off')

            # WAS OFF >> ON
            elif items.iPhone.status == False: # was off
                iPhone_connection(True)
                if TW.IsItDark() and  items.lamp.status == False: #!!!: doesn't work > check total dark
                    if timer.lamp.CheckDelay():
                        sleep(0.1); os.system('curl http://192.168.1.176/control/rf433/light/on')
                        Speak('lights on')
                        items.lamp.status = True

            #updating status
            items.iPhone.status = iPhone.Status()

    # twilight
    if twilight:
        if TW.IsItTwilight('morning'):
            if timer.lamp.CheckDelay():
                logger.info('TwilightSwitcher morning')
                Speak('it is sunrise')
                sleep(0.1); os.system('curl http://192.168.1.176/control/rf433/light/off')
                items.lamp.status = False
        if  TW.IsItTwilight('evening'):
            logger.info('TwilightSwitcher evening, iPhone status {}'.format(iPhone.Status()))
            if  iPhone.Status():  #!!!: items.lamp.status == False --- lets turn it off even if it was off
                if timer.lamp.CheckDelay():
                    sleep(0.1); os.system('curl http://192.168.1.176/control/rf433/light/on')
                    items.lamp.status = True
                    Speak("it is sunset")

    return iPhone.Pause([10,50]) # offline (searching) / online skipping minute

def iPhone_connection(status):
    "True / False"
    for a in range(0,3):
        try:
            sleep(0.1); requests.get('http://192.168.1.176/control/rf433/i_am_home/' + ('on' if status else 'off'))
            sleep(0.1); requests.get('http://192.168.1.176/control/color/' + ('green' if status else 'red'))
            Speak('iPhone ' + ('connected' if status else 'connection lost'))
            logger.info('iPhone '+ ('connected' if status else 'connection lost'))
            return
        except:
            pass



#%%
if __name__ == '__main__':
    logger = LOGGER('pa_service', level = 'INFO')
    p = CONFIGURATION()

    timer = OBJECT({'iPhone':       TIMER(60, [0,1,2,3,4]),
                    'iCloud_cal':   TIMER(60*5), #testing 10 (was 5)
                    'iCloud_photo': TIMER(60*15), #testing 10 (was 5)
                    'reminders' :   TIMER(60, [23,0,1,2,3,4]),
                    'Sun' :         TIMER(60),
                    'speak' :       TIMER(60),
                    'lamp' :        TIMER(60),
                    'CheckTime' :   CheckTime})
    try:
        pa_reAuth()
    except:
        MainException()
