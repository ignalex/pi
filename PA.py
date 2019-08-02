# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 10:19:08 2014

@author: aignatov
"""
#DONE: bad design > all reimporting all time - run from CMD not good.

from __future__ import print_function

import sys, os
from time import sleep
from modules.common import  LOGGER, CONFIGURATION, MainException, Dirs

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

from modules.control_esp import ESP as esp  #control_esp as ESP
from modules.PingIPhone import AcquireResult #FIXME: this will crash octopus

import __main__ as m


def Event (args):
    module, p  = args.split('_')[0], args.split('_')[1:]
    m.logger.info('module ' + module + ', args ' + str(p))
    try:
        if len(args.split('_')) == 1 and module in globals(): # no arguments
            try:
                globals()[module]([''])
            except:
                m.logger.error('error in module ' + module )
                MainException()
        elif module in globals():
            m.logger.info('module imported')
            globals()[module](p)
        else:
            m.logger.info('>>> to general')
            GENERAL([module])
    except:
        m.logger.error('error in module ' + module + ' ' + str(sys.exc_info()))

def PA():
    TASKS = [item for sublist in [i.split(':') for i in [j.upper() for j in sys.argv[1:] if j!='-d']] for item in sublist] # taking args and splitting by :
    m.logger.debug(str(TASKS))
    for task in TASKS:
        m.logger.debug(str(task))
        Event(task)
        m.logger.debug(str(task) + ' . ')
        sleep(1)

def GENERAL(arg):
    try:
        m.logger.debug( str(arg))
        Phrase({'TYPE' : arg[0]}) # speak phrase if nothing else.
    except Exception as e:
        m.logger.error( str(e) )
        MainException()

def TIME(arg):
    a  = 'HM' if (len(arg) == 0 or arg is None) else ('HM' if arg[0] == '' else arg[0])
    return Phrase({'TYPE' : 'TIME_'+ a})

def RUTIME(arg):
    try:
        m.logger.debug(str(arg))
        if arg[0] == '': arg[0] = 'HM'
        Phrase({'TYPE' : 'RUTIME_'+arg[0]})
    except:
        MainException()

def TEMP(arg):
    if arg ==  []: arg = ['ALL']
    w = WEATHER_class()
    w.ToInt()
    Phrase({'TYPE' : 'INSIDE_TEMP', 'T' : str(w.temp_in)})
    if arg[0] != 'IN':
        sleep(1)
        return Phrase({'TYPE' : 'OUTSIDE', 'T' : str(w.temp_out),'HUM' : str(w.humidity) })

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

def WEATHERYAHOO(arg):
    w = weather_yahoo()
    m.logger.debug('w element ok')
    Speak(w.all, store=False) # cause filename <250
    m.logger.debug('spoken done')

def MAIL(arg):
    if 'EMAIL' in p.INI.keys() and p.INI['EMAIL'] != 'NO':
        m.logger.info( 'mailing to ' + p.INI['EMAIL'] + ' file ' + str(arg[0]) + ' located at ' + str(p.INI[arg[0]]))
        status = []
        if len(arg) > 1:
            subj = arg[1]
        else:
            subj = arg[0]
        for recepient in  p.INI['EMAIL'].split(','):
            status.append(sendMail([recepient],p.INI['SMTP'].split(','), subj,'' , p.INI[arg[0]].split(';')))


#def MONEYREPORT(arg = ''):
#    today_file = p.INI['MONEY_REPORT']
#    spendings = [(i.split(' ')[2].replace('_',' '),i.split('\t')[-3].replace('-','')) for i in [i for i in open(today_file,'r').read().splitlines() if i.startswith('20')]]
#    delta = [i for i in open(today_file,'r').read().splitlines() if i.startswith('DELTA')][0].replace('DELTA', 'Delta on the end of the year is ')
#    if spendings != []:
#        Phrase({'TYPE': 'TODAY_SPENDINGS'})
#        for sp in spendings: Speak(' '.join(sp))
#    Speak(delta)

def REMINDER(arg):
    #DONE: work only with iPone connected
    if AcquireResult(): # reading last reading iPhone reading
        if int(arg[1]) % 60 == 0:
            h = str(int(arg[1]) / 60)
            if h == 1:
                end = ''
            else:
                end = 's'
            return Phrase({'TYPE' : 'REMINDER_H', 'ACTION' : arg[0].replace('-',' '),'LEFT' : h, 'END' : end})
        else:
            return  Phrase({'TYPE' : 'REMINDER', 'ACTION' : arg[0].replace('-',' '),'LEFT' : arg[1]})
    else:
        m.logger.debug('reminder NOT spoken > iPhone not around')

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

def SPENDINGS(args):
    text = [i for i in open(os.path.join(Dirs()['SPENDINGS'],'today.txt'),'r').read().splitlines() if i != '']
    res = []
    for t in text:
        res.append(Speak(t)['text'])
    return {'status': True, 'text' : '; '.join(res)}

def ALLEVENTSTODAY(args):
    "speak all events from the iCloud calendar"
    #TODO: instead of initiating new connection, use the pa_service
    events = AllEvents()
    if events not in [None,'']:
        Speak('today planned in your calendar. ' + str(events)) # translating unicode to str > otherwise error
#
#def CAMERA(args):
#    m.logger.info('capturing pic from octopus')
#    os.system("ssh -p 2227 -i /home/pi/.ssh/octopus pi@192.168.1.154 nohup python /home/pi/PYTHON/GPIO/modules/camera.py &")
#    m.logger.info('done')
##

# -----------------------------------------------

if __name__ == '__main__':
    logger = LOGGER('pa', 'INFO')
    p = CONFIGURATION()

    try: #FIXME: with daemon works very slow
#        try:
#            import daemon
#            with daemon.DaemonContext(files_preserve = [m.logger.handlers[0].stream,]):
#                m.logger.debug('PA with daemon')
#                PA()
#        except:
            m.logger.debug('PA without daemon')
            PA()
    except:
        MainException()