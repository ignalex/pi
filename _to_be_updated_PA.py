# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 10:19:08 2014

@author: aignatov
"""
import sys, os,  subprocess
from time import sleep 
sys.path.append('/storage/PY_modules/') # for OpenElec
try: 
    sys.path.append( [i for i in ['/home/pi/PYTHON/GPIO/','/storage/PYTHON/GPIO/', 'C:\\Users\\aignatov\\Dropbox\\PI\\GPIO','E:\\dropbox_AI\\Dropbox\\PI\\GPIO'] if os.path.exists(i) == True][0]) 
except: 
    print 'NO SELF PATH CONFIGURED'
    sys.exit()
   
from modules.SHELL import SimpleIni, LOGGER, PID, ReadFileBySSH, PARAMETERS, MainException
#loging = LOGGING('PA')
PID()
self_path = os.getcwd()

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from modules.talk import Speak, Phrase#, TALKING_PARAMETERS
#talk_params = TALKING_PARAMETERS()
from modules.send_email_v2 import sendMail
from modules.mod_spatial import Distance, PointToKML
from modules.iCloud import (InstantLocation, iCloudConnect, AllEvents)
from modules.weather import WEATHER as WEATHER_class
from heater import TranslateForHornet as HEATER
from modules.slang import SLANG
from modules.control_esp import ESP as esp #control_esp as ESP 

#class PARAMETERS (object): 
#    def __init__(self, ID = ''):
#        self.current_time = datetime.datetime.now()
##        self.pause = 1
#        self.INI = SimpleIni('PA.INI')
#        for p in ['DAEMON', 'SIMULATE','DEBUG']: setattr(self, p, [True if i == 'YES' else False for i in [self.INI[p]]][0])

class PLACES (object): 
    def __init__(self):
        self.LOCATIONS = SimpleIni('locations.INI')
        

#def ReadLastTemp(minutes):
#    try: 
#        current = LastLine(params.INI['TEMPERATURE'])
#    except: 
#        print 'no TEMP file available' 
#        return [False]
#        
#    last_time = datetime.datetime.strptime(current.split('\t')[0], '%Y-%m-%d %H:%M')
#    
#    if (params.current_time - last_time).seconds/60 <= minutes:  
#        return current.split('\t')[1:]
#    else: 
#        return [False]

def Event (args): 
    module, params  = args.split('_')[0], args.split('_')[1:]
    logger.info('module ' + module + ', args ' + str(params))
    try: 
        if len(args.split('_')) == 1 and module in globals(): # no arguments 
            try:
                globals()[module]([''])
            except: 
                logger.error('error in module ' + module + ' ' + str(sys.exc_info()))
        elif module in globals(): 
            logger.info('module imported')
            globals()[module](params)
        else: 
            logger.info('to general')
            GENERAL([module])
    except: 
        logger.error('error in module ' + module + ' ' + str(sys.exc_info()))
        #GENERAL([module])

def PA(): 
    TASKS = [item for sublist in [i.split(':') for i in [j.upper() for j in sys.argv[1:]]] for item in sublist] # taking args and splitting by : 
    log(str(TASKS))
    for task in TASKS: 
        if params.DEBUG: log(str(task))
        Event(task)
        if params.DEBUG: log(str(task) + ' . ')
        sleep(int(params.PAUSE))
            
# -----------------------------------------------
def GENERAL(arg): 
    try: 
        if params.DEBUG: print 'GENERAL', arg
        Phrase({'TYPE' : arg[0]})
    except: 
        print 'nothing suitable found in the dict'
     
def TIME(arg):
    if arg[0] == '': arg[0] = 'HM'
    Phrase({'TYPE' : 'TIME_'+arg[0]})   

def TEMP(arg): 
    w = WEATHER_class()
    w.ToInt()
    Phrase({'TYPE' : 'INSIDE_TEMP', 'T' : str(w.temp_in)})
    if arg[0] != 'IN':         
        sleep(int(params.PAUSE))      
        Phrase({'TYPE' : 'OUTSIDE', 'T' : str(w.temp_out),'HUM' : str(w.humidity) })

def WEATHER(arg): 
    w = WEATHER_class()
    w.ToInt()
    if params.DEBUG: log('weather read and parsed ' +  '\t'.join([str(w.temp_out) , str(w.humidity) ,  str(w.pressure) , str(w.rain) , str(w.forecast) , str(w.temp_today)]))
    if w.rain_at_all:
        Phrase({'TYPE' : 'WEATHER1', 'TEMP' : str(w.temp_out),'HUM' : str(w.humidity), 'PR' : str(w.pressure), \
                'RAIN' : str(w.rain), 'FORECAST': str(w.forecast),'TMAX' : str(w.temp_today), \
                'WIND' : str(w.wind), 'WND_GUST' : str(w.wind_gust)})
    else: 
        Phrase({'TYPE' : 'WEATHER2', 'TEMP' : str(w.temp_out),'HUM' : str(w.humidity), 'PR' : str(w.pressure), \
                'FORECAST': str(w.forecast),'TMAX' : str(w.temp_today), 'WIND' : str(w.wind), 'WND_GUST' : str(w.wind_gust)  })
        
def MAIL(arg): 
    if 'EMAIL' in params.INI.keys() and params.INI['EMAIL'] != 'NO': 
        log( 'mailing to ' + params.INI['EMAIL'] + ' file ' + str(arg[0]) + ' located at ' + str(params.INI[arg[0]]))  
        status = []
        if len(arg) > 1: 
            subj = arg[1]
        else: 
            subj = arg[0]
        for recepient in  params.INI['EMAIL'].split(','): 
            status.append(sendMail([recepient],params.INI['SMTP'].split(','), subj,'' , params.INI[arg[0]].split(';')))

def R(arg): 
    if 'R' in params.INI.keys() and params.INI['R'] =='YES': 
        rscript = arg[0] #, arg[1]
        if params.DEBUG: 
            log( str(rscript ) + ' ' + str( params.INI[rscript])) 
        if not params.SIMULATE: 
            subprocess.call(["Rscript",params.INI[rscript]], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def MONEYREPORT(arg = ''): 
    today_file = params.INI['MONEY_REPORT']
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

def PROX(arg): 
    PROXIMITY(arg)

def ESP(arg): 
    # FIXME: handle capitals 
    arg = [i.lower() for i in arg]
    e = esp()
#    e.Go(arg )
    e.Go_parallel(arg )
    
def PROXIMITY(arg): 
    """pa proximity_home_100_me
    """
    places = PLACES()
    if params.DEBUG: log(str(places.LOCATIONS))
    destination = float(places.LOCATIONS[arg[0]].split(',')[0]),float(places.LOCATIONS[arg[0]].split(',')[1])
    distance_report = int(arg[1]) # meters 
    log('looking for destination ' + arg[0] + ' : distance = ' + str(distance_report))
    params.iCloudApi = iCloudConnect()
    while True: 
        loc = [float(i) for i in InstantLocation(params.iCloudApi)]
        dist = int(Distance(loc, destination)) 
        log(str(loc) + ' : ' + str(dist))
        if dist <= distance_report:
            log_string = 'PROXIMITY: position ' + str(loc) + ' is ' + str(dist) + 'm. from ' + arg[0]
            log(log_string)
            #sendMail([params.INI['EMAIL']],params.INI['SMTP'].split(','), 'PROXIMITY',log_string , [])
            if params.DEBUG: log(str(arg))
            if len(arg) == 3: 
                address = SimpleIni('contacts.INI')[arg[2]]
                kml = PointToKML(loc,os.path.join('/home/pi/tracking','location.kml'))
                sendMail([address],params.INI['SMTP'].split(','), 'Alex is in' + str(dist) + ' m. from ' + arg[0], log_string , [kml])
                log('email sent to ' + address) 
            break 
        sleep(int(params.INI['TRACKING_INTERVAL']))

def SPENDINGS(args): 
    text = [i for i in ReadFileBySSH().splitlines() if i != '']
    for t in text:  Speak(t)

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
    params = PARAMETERS('PA.INI')
    logger = LOGGER('PA.txt', 'INFO',True)
    log = logger.info

    try: 
        if params.DAEMON == True: 
            import daemon
            with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
                PA() 
        else: 
            PA()
    except: 
        MainException()