# -*- coding: utf-8 -*-
"""
Managing Services
triggering functions:

based on conditions

Created on Tue Apr 22 19:31:53 2014
@author: ignalex
v4. - movement + standby + lamp
v5. - pins defined in the INI file + >>> all into submodules
v5.1. - with relay init status
v6 - one event can be programmed + re-erite code
v7 - bluetooth scanning
v9 - migrated to git

crontab config:

#MS
00 04 * * 1-5 sudo python /home/pi/git/pi/MS.py 12.99h a:: pass once m:: lamp ON + pa morning:time:temp_in:weather:alleventstoday:spendings:protein once + esp 6_rf433_coffee_on once s:: lamp OFF + esp 6_rf433_coffee_off once
00 17 * * 1-5 sudo python /home/pi/git/pi/MS.py 6h a:: pass m:: lamp ON + pa welcome:temp_in once s:: lamp OFF
00 04 * * 6,7 sudo python /home/pi/git/pi/MS.py 19h a:: pass m:: lamp ON + pa morning:temp_in:weather:alleventstoday:spendings:protein once + esp 6_rf433_coffee_on once s:: lamp OFF + esp 6_rf433_coffee_off once
"""
#TODO: on start first check status Iphone
#TODO: on start delay actions? why trigger...?

from __future__ import print_function
import __main__ as m

import sys, datetime
from time import sleep
from threading import Thread
from modules.common import  LOGGER, PID, CONFIGURATION, MainException

logger = LOGGER('ms', level = 'INFO')
p = CONFIGURATION() #pins

from modules.sunrise import Sun
#    from modules.mod_movement_email import mail #TODO: email mod and phrase
#from modules.KODI_control import kodi
#from modules.wol import wol
from modules.talk import Phrase
from modules.pa import pa
from modules.pa import pa as pa1 #!!!: quick fix
from modules.PingIPhone import PING
from modules.control_esp import ESP

#%% def
class ARGUMENTS(object):
    def __init__(self):
        self.raw = ' '.join(sys.argv[2:])
        self.once = {}
        self.Process('alarm',str(self.raw[self.raw.find('a::')+4 : self.raw.find('m::')-1]).split(' + ')) # all records must start from a:
        self.Process('move', str(self.raw[self.raw.find('m::')+4 : self.raw.find('s::')-1]).split(' + '))
        self.Process('stb',  str(self.raw[self.raw.find('s::')+4:]).split(' + '))
    def Process(self,act,arg):
        d = {}
        for a in arg:
            if len(a.split(' ')) == 1:
                d[a] = ''
            else: # 1 or more args
                if 'once' in a.split(' '):
                    self.once[' '.join([i for i in a.split(' ') if i !='once'])] = 1
                d[a.split(' ')[0]] = ''.join([i for i in a.split(' ')[1:] if i !='once'])
        setattr(self,act,d)

class OBJECT(object):
    def __init__ (self):
        pass
    def Child (self, name, status):
        setattr(self,name, ITEM(name,status))
    def Available(self):
        self.available = [i for i in self.__dict__.keys() if i not in ['available','GLOBAL']]

class ITEM (object):
    def __init__ (self,name,status):
        self.name = name
        self.status = status

class TIMING (object):
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.last_reading = self.start_time
        self.fire_time = float(sys.argv[1].replace('h','')) * 3600 - 120 # 1 min less - to avoid overlapping the cycles
        self.twilight = Sun(datetime.date.today())
        self.no_movement_trigger = False
        self.exclusion_times =['7.05','23.00','19.05']
        self.count_move = 0
    def Move(self):
        self.last_reading = datetime.datetime.now()
        Blink()
        self.count_move +=1
        self.no_movement_trigger = True
    def GlobalStop(self): # returns True if to proceed
        return self.start_time + datetime.timedelta(seconds = self.fire_time) > datetime.datetime.now()
    def TwilightSwitcher(self,twilight): # return moment to turn OFF / OM the lights (1 min only)
        n = {'morning':0,'evening':1 , 'windows_light' : 2,'total_dark' : 3}[twilight]
        return datetime.datetime.now().hour == self.twilight[n].hour and datetime.datetime.now().minute == self.twilight[n].minute
    def Proceed(self): # set of conditions to proceed with event or not.
        if True in [datetime.datetime.now().hour == int(i.split('.')[0]) and  datetime.datetime.now().minute == int(i.split('.')[1]) for i in self.exclusion_times]:
            return False # don't proceed if time excluded
        else:
            return True
    def IamAround(self,minutes): # movement has been registered N min ago + at least once
        if self.count_move != 0 and (self.last_reading + datetime.timedelta(minutes = minutes) <=  datetime.datetime.now()):
            return True
        else:
            return False
#%% GPIO
import RPi.GPIO as GPIO # if there is error on import not found RPI - need to enable device tree from raspi-config
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.INIT = GPIO.HIGH
GPIO.ON = GPIO.LOW
GPIO.OFF = GPIO.HIGH

GPIO.setup(p.pins.BLINK, GPIO.OUT, initial = GPIO.INIT)
GPIO.setup(p.pins.MOVEMENT_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP) #DONE: UP works

#%% extra modules
def Blink(args = [1,1,0.1]):
    for b in range(int(args[0])):
        for a in range(int(args[1])):
            GPIO.output(p.pins.BLINK, GPIO.HIGH)
            sleep(float(args[2]))
            GPIO.output(p.pins.BLINK, GPIO.LOW)
            sleep(float(args[2]))
        if int(args[0]) != 1: sleep(0.3)

#def play(TASK = ['play_current']):
#    wip = kodi('what_is_playing')
#    m.logger.info('TASK recieved: ' + TASK[0] + ', wip answer: '+ wip)
#    if TASK == ['pause']:
#        if wip == 'audio':
#            kodi('pause')
#            m.logger.info('pausing music')
#            m.items.play.status = False
#        elif wip == 'video':
#            m.logger.info('video is playing. Won\'t stop')
#        elif wip == 'nothing':
#            m.logger.info('nothing is playing')
#    else:
#        if wip == 'nothing':
#            kodi(TASK[0])
#            m.logger.info('starting playing current')
#            m.items.play.status = True
#        elif wip == 'audio':
#            kodi('resume')
#            m.logger.info('resuming audio')
#            m.items.play.status = True
#        elif wip == 'video':
#            m.logger.info('video is current. won\'t do anything')

def lamp(TASK):
    "to be used only from inside MS"
    "dependencies: esp, log, sunrise"
    if TASK == []:
        m.logger.info('Lamp module: Not enough argument')

    twilight = m.Sun(datetime.date.today())
    now = datetime.datetime.now()

    if TASK == ['ON'] and (now <= twilight[0] or now >= twilight[1]): # turm ON only if dark
        # lamp ON
        m.items.lamp.status = True
        m.logger.info( 'lamp ON')
        try:
            m.ESP(['6','rf433','light','on'])
            m.logger.info('lamps are ON')
        except:
            pass
    elif TASK == ['ON'] and (now > twilight[0] and now < twilight[1]):
        m.logger.info('day time. Lamp is not turned ON')
    elif TASK == ['OFF']: # turn OFF at any time
        # lamp off
        m.items.lamp.status = False
        m.logger.info( 'lamp OFF')
        try:
            m.ESP(['6','rf433','light','off'])
            m.logger.info('lamps are OFF')
        except:
            pass

def esp(TASK):
    TASK = TASK[0].split('_')
    m.logger.info('esp task : ' + str(TASK))
    ESP(TASK)
    #DONE: fix ESP 175 code / return bad > need to update

#%%
def Event(channel):
    if timing.Proceed(): Movement()

def ThreadedEvent (args): # args is module +' ' + param OR module
    module = args.split(' ')[0]
    if args in control.once.keys():
        if control.once[args] == 0:
            logger.info(args + ' already had ONE go. skipping.' )
            return
        else:
            logger.info('ONLY one time for ' + args)
            control.once[args] -=1
    try:
        arguments = args.split(' ')[1:]
        globals()[module](arguments)
    except:
        globals()[module]()

def Movement():
    if iPhone.Status(): # movement module
        Movement_by_category(category = 'move')
        items.GLOBAL.status = True
        timing.Move()
    else: # alarm module
        Movement_by_category(category = 'alarm')
        timing.Move()

def Movement_by_category(category = 'move', mod_stat = False):
    "trigger for 'move' OR 'alarm' or 'stb' "
    th, to_log = [], []
    if 'pass' not in getattr(control, category).keys():
        if category == 'move' and items.GLOBAL.status != False: return # only for move early exit

        for mod,arg in sorted(getattr(control, category).items()): #added sorted here
            if mod in items.available:
                if getattr(getattr(items,mod),'status') == mod_stat:
                    th.append( Thread(target = ThreadedEvent, args = [' '.join([mod,arg]).rstrip()]))
                    to_log.append(' '.join([mod,arg]))
                else:
                    pass
            else: # not in the list of items where status is controlled
                th.append( Thread(target = ThreadedEvent, args = [' '.join([mod,arg]).rstrip()]))
                to_log.append(' '.join([mod,arg]))
        logger.info(category.upper()+ ':\t' +', '.join(to_log))
    else:
        logger.info('passing')
    for t in th: t.start() #starting all
    for t in th: t.join()  #finishing all


def iPhone_connection_lost():
    Movement_by_category(category = 'stb', mod_stat = True)
    items.GLOBAL.status = False
    timing.no_movement_trigger = False

GPIO.add_event_detect(p.pins.MOVEMENT_SENSOR, GPIO.RISING, callback=Event, bouncetime=1500) # RISING works

#%% main
def main():
    # loop
    while timing.GlobalStop():
        iPhone.Ping()
        if iPhone.changed != None:
            ESP(['6', 'color',  ['green' if i else 'red' for i in [iPhone.changed]][0]],'0') # ESP indicator on 5 esp
            ESP(['6','rf433','13', ['1' if i else '0' for i in [iPhone.changed]][0]]) #['6','rf433','3','0'] # power #3 fire
            logger.info('iPhone status changed to ' + str(iPhone.changed))
        if iPhone.status == False:
            ThreadedEvent('Blink 1 1 0.3')
        if timing.count_move == 0:
            ThreadedEvent('Blink 1 3 0.3')
        if timing.no_movement_trigger:
            if  iPhone.Status() == False: #  checking considering delay
                logger.info('iPhone - contact lost')
                iPhone_connection_lost()
        if 'lamp' in control.move.keys():
            if timing.TwilightSwitcher('morning') and items.lamp.status:
                logger.info('TwilightSwitcher morning')
                lamp(['OFF'])
                items.lamp.status = False
            if  timing.TwilightSwitcher('evening') and items.lamp.status == False and iPhone.Status():# timing.IamAround(30):
                lamp(['ON'])
                timing.Move()
                items.lamp.status = True
        sleep(iPhone.Pause([5,45]))  #was 5 - 30

    # finishing
#    if ('play' in control.move.keys() or 'play' in control.stb.keys()) and items.play.status: play(['pause'])
    if 'lamp' in control.move.keys(): lamp(['OFF'])
    if datetime.datetime.now().hour >= 20: Phrase({'TYPE' :'GOOD_NIGHT'})

    logger.info ('finishing '+ sys.argv[0])

    GPIO.cleanup(p.pins.MOVEMENT_SENSOR)
    ESP(['6', 'color', 'off', '0'])
    Phrase({'TYPE' : 'EXIT_MS'})

#%% start
if __name__ == '__main__':
    try:
        # setting up
        if len(sys.argv) < 2 :
            logger.error( 'not enough arguments')
            sys.exit()

        PID()
        control = ARGUMENTS()
        timing  = TIMING()
        items   = OBJECT()
        iPhone  = PING()

        for mods in ['GLOBAL','lamp','play']: items.Child(mods,False)
        items.Available()

        logger.info('\n')
        logger.info ('started ' + ' '.join(sys.argv) )
        logger.info ('on alarm '.upper() + str(control.alarm))
        logger.info ('on move '.upper() + str(control.move))
        logger.info ('on standby '.upper() + str(control.stb))
        logger.info ('once '.upper() + str(control.once))
        logger.info ('Fire time: '+ str((timing.fire_time/3600)) + ' hours' )
        #Phrase({'TYPE' : 'START_MS'})
        #self_path = os.path.dirname(sys.argv[0])

        main()
    except:
        MainException()
