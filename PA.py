# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 10:19:08 2014

@author: aignatov
"""
from __future__ import print_function

import sys, os
from time import sleep
from modules.common import  LOGGER, CONFIGURATION, MainException

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from modules.talk import Speak, Phrase
from modules.send_email import sendMail
#from modules.mod_spatial import Distance, PointToKML
from modules.iCloud import AllEvents#(InstantLocation, iCloudConnect, AllEvents)
from modules.weatherzone import WEATHER as WEATHER_class
try:
    from modules.weather_yahoo import weather_yahoo
except:
    pass
#from heater import TranslateForHornet as HEATER
#from modules.slang import SLANG
from modules.control_esp import ESP as esp  #control_esp as ESP

#class PARAMETERS (object):
#    def __init__(self, ID = ''):
#        self.current_time = datetime.datetime.now()
##        self.pause = 1
#        self.INI = SimpleIni('PA.INI')
#        for p in ['DAEMON', 'SIMULATE','DEBUG']: setattr(self, p, [True if i == 'YES' else False for i in [self.INI[p]]][0])

#class PLACES (object):
#    def __init__(self):
#        self.LOCATIONS = SimpleIni('locations.INI')


#def ReadLastTemp(minutes):
#    try:
#        current = LastLine(p.INI['TEMPERATURE'])
#    except:
#        print 'no TEMP file available'
#        return [False]
#
#    last_time = datetime.datetime.strptime(current.split('\t')[0], '%Y-%m-%d %H:%M')
#
#    if (p.current_time - last_time).seconds/60 <= minutes:
#        return current.split('\t')[1:]
#    else:
#        return [False]

def Event (args):
    module, p  = args.split('_')[0], args.split('_')[1:]
    logger.info('module ' + module + ', args ' + str(p))
    try:
        if len(args.split('_')) == 1 and module in globals(): # no arguments
            try:
                globals()[module]([''])
            except:
                logger.error('error in module ' + module + ' ' + str(sys.exc_info()))
        elif module in globals():
            logger.info('module imported')
            globals()[module](p)
        else:
            logger.info('to general')
            GENERAL([module])
    except:
        logger.error('error in module ' + module + ' ' + str(sys.exc_info()))

def PA():
    TASKS = [item for sublist in [i.split(':') for i in [j.upper() for j in sys.argv[1:] if j!='-d']] for item in sublist] # taking args and splitting by :
    logger.debug(str(TASKS))
    for task in TASKS:
        logger.debug(str(task))
        Event(task)
        logger.debug(str(task) + ' . ')
        sleep(1)

def GENERAL(arg):
    try:
        logger.debug( str(arg))
        Phrase({'TYPE' : arg[0]}) # speak phrase if nothing else.
    except:
        logger.error( 'nothing suitable found in the dict' )

def TIME(arg):
    if arg[0] == '': arg[0] = 'HM'
    Phrase({'TYPE' : 'TIME_'+arg[0]})

def RUTIME(arg):
    try:
        logger.debug(str(arg))
        if arg[0] == '': arg[0] = 'HM'
        Phrase({'TYPE' : 'RUTIME_'+arg[0]})
    except:
        MainException()

def TEMP(arg):
    w = WEATHER_class()
    w.ToInt()
    Phrase({'TYPE' : 'INSIDE_TEMP', 'T' : str(w.temp_in)})
    if arg[0] != 'IN':
        sleep(1)
        Phrase({'TYPE' : 'OUTSIDE', 'T' : str(w.temp_out),'HUM' : str(w.humidity) })

def WEATHER(arg):
    w = WEATHER_class()
    w.ToInt()
    logger.debug('weather read and parsed ' +  '\t'.join([str(w.temp_out) , str(w.humidity) ,  str(w.pressure) , str(w.rain) , str(w.forecast) , str(w.temp_today)]))
    if w.rain_at_all:
        Phrase({'TYPE' : 'WEATHER1', 'TEMP' : str(w.temp_out),'HUM' : str(w.humidity), 'PR' : str(w.pressure), \
                'RAIN' : str(w.rain), 'FORECAST': str(w.forecast),'TMAX' : str(w.temp_today), \
                'WIND' : str(w.wind), 'WND_GUST' : str(w.wind_gust)})
    else:
        Phrase({'TYPE' : 'WEATHER2', 'TEMP' : str(w.temp_out),'HUM' : str(w.humidity), 'PR' : str(w.pressure), \
                'FORECAST': str(w.forecast),'TMAX' : str(w.temp_today), 'WIND' : str(w.wind), 'WND_GUST' : str(w.wind_gust)  })

def WEATHERYAHOO(arg):
    w = weather_yahoo()
    logger.debug('w element ok')
    Speak(w.all, store=False) # cause filename <250
    logger.debug('spoken done')

def MAIL(arg):
    if 'EMAIL' in p.INI.keys() and p.INI['EMAIL'] != 'NO':
        logger.info( 'mailing to ' + p.INI['EMAIL'] + ' file ' + str(arg[0]) + ' located at ' + str(p.INI[arg[0]]))
        status = []
        if len(arg) > 1:
            subj = arg[1]
        else:
            subj = arg[0]
        for recepient in  p.INI['EMAIL'].split(','):
            status.append(sendMail([recepient],p.INI['SMTP'].split(','), subj,'' , p.INI[arg[0]].split(';')))


def MONEYREPORT(arg = ''):
    today_file = p.INI['MONEY_REPORT']
    spendings = [(i.split(' ')[2].replace('_',' '),i.split('\t')[-3].replace('-','')) for i in [i for i in open(today_file,'r').read().splitlines() if i.startswith('20')]]
    delta = [i for i in open(today_file,'r').read().splitlines() if i.startswith('DELTA')][0].replace('DELTA', 'Delta on the end of the year is ')
    if spendings != []:
        Phrase({'TYPE': 'TODAY_SPENDINGS'})
        for sp in spendings: Speak(' '.join(sp))
    Speak(delta)

def REMINDER(arg):
    if int(arg[1]) % 60 == 0:
        h = str(int(arg[1]) / 60)
        if h == 1:
            end = ''
        else:
            end = 's'
        Phrase({'TYPE' : 'REMINDER_H', 'ACTION' : arg[0].replace('-',' '),'LEFT' : h, 'END' : end})
    else:
        Phrase({'TYPE' : 'REMINDER', 'ACTION' : arg[0].replace('-',' '),'LEFT' : arg[1]})

def ESP(arg):
    arg = [i.lower() for i in arg]
    e = esp()
    e.Go_parallel(arg )


#def PROX(arg):
#    PROXIMITY(arg)

#def PROXIMITY(arg):
#    """pa proximity_home_100_me
#    """
#    places = PLACES()
#    if p.DEBUG: log(str(places.LOCATIONS))
#    destination = float(places.LOCATIONS[arg[0]].split(',')[0]),float(places.LOCATIONS[arg[0]].split(',')[1])
#    distance_report = int(arg[1]) # meters
#    log('looking for destination ' + arg[0] + ' : distance = ' + str(distance_report))
#    p.iCloudApi = iCloudConnect()
#    while True:
#        loc = [float(i) for i in InstantLocation(p.iCloudApi)]
#        dist = int(Distance(loc, destination))
#        log(str(loc) + ' : ' + str(dist))
#        if dist <= distance_report:
#            log_string = 'PROXIMITY: position ' + str(loc) + ' is ' + str(dist) + 'm. from ' + arg[0]
#            log(log_string)
#            #sendMail([p.INI['EMAIL']],p.INI['SMTP'].split(','), 'PROXIMITY',log_string , [])
#            if p.DEBUG: log(str(arg))
#            if len(arg) == 3:
#                address = SimpleIni('contacts.INI')[arg[2]]
#                kml = PointToKML(loc,os.path.join('/home/pi/tracking','location.kml'))
#                sendMail([address],p.INI['SMTP'].split(','), 'Alex is in' + str(dist) + ' m. from ' + arg[0], log_string , [kml])
#                log('email sent to ' + address)
#            break
#        sleep(int(p.INI['TRACKING_INTERVAL']))

#def SPENDINGS(args):
#    text = [i for i in ReadFileBySSH().splitlines() if i != '']
#    for t in text:  Speak(t)

def ALLEVENTSTODAY(args):
    "speak all events from the iCloud calendar"
    events = AllEvents()
    if events not in [None,'']:
        Speak('today planned in your calendar. ' + str(events)) # translating unicode to str > otherwise error

def CAMERA(args):
    logger.info('capturing pic from octopus')
    os.system("ssh -p 2227 -i /home/pi/.ssh/octopus pi@192.168.1.154 nohup python /home/pi/PYTHON/GPIO/modules/camera.py &")
    logger.info('done')


# -----------------------------------------------

if __name__ == '__main__':
    logger = LOGGER('PA', 'INFO')
    p = CONFIGURATION()

    try: #FIXME: with daemon works very slow
#        try:
#            import daemon
#            with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
#                logger.debug('PA with daemon')
#                PA()
#        except:
            logger.debug('PA without daemon')
            PA()
    except:
        MainException()