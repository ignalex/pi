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
"""   
from __future__ import print_function
 
import __main__ as m 

class ARGUMENTS(object): 
    def __init__(self): 
        self.raw = ' '.join(sys.argv[2:])
        self.once = {}
        self.Process('alarm',str(self.raw[self.raw.find('a:')+3 : self.raw.find('m:')-1]).split(' + ')) # all records must start from a:
        self.Process('move', str(self.raw[self.raw.find('m:')+3 : self.raw.find('s:')-1]).split(' + '))
        self.Process('stb',  str(self.raw[self.raw.find('s:')+3:]).split(' + '))
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
#        self.delay_time = float(sys.argv[2].replace('m','')) * 60
        self.twilight = Sun(datetime.date.today())
        self.no_movement_trigger = False 
        self.exclusion_times =['7.05','23.00','19.05']
        self.count_move = 0 
    def Move(self): 
        self.last_reading = datetime.datetime.now()
#        ThreadedEvent('Blink 1 1 0.3')
        Blink()
#        stat()
        self.count_move +=1
        self.no_movement_trigger = True 
    def GlobalStop(self): # returns True if to proceed 
        return self.start_time + datetime.timedelta(seconds = self.fire_time) > datetime.datetime.now()
#    def NoMovement(self): # return True when NO MOVEMENT and needed action 
#        return self.last_reading + datetime.timedelta(seconds = self.delay_time) <=  datetime.datetime.now()
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
      
try: 
    ################################# IMPORT ######################################
    # IMPORTING INITIAL MODULES 
    import sys, os, datetime
    from time import sleep 
#    from os.path import join 
    from threading import Thread 
    from modules.common import  LOGGER, PID, CONFIGURATION, MainException
    logger = LOGGER('MS', level = 'INFO') 
    log = logger.info
#    loging = logger # compatibility 
    PID()
    
    sys.path.append(os.path.dirname(sys.argv[0])) # path to 'modules' subfolder 
    self_path = os.path.dirname(sys.argv[0])       
    if len(sys.argv) < 2 : 
        logger.info( 'not enough arguments')
        sys.exit()
    
    # IMPORTING GPIO MODULES 
    import RPi.GPIO as GPIO # if there is error on import not found RPI - need to enable device tree from raspi-config
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    #TODO: email mod and phrase 
    
    # IMPORTING SUBMODULES 
    from modules.sunrise import Sun
#    from modules.mod_movement_email import mail
    from modules.KODI_control import kodi
    from modules.wol import wol
#    from modules.ard import ard
    from modules.ms_lamp import lamp    #FIXME: move 
    from modules.speak_over_ssh import Phrase #FIXME: from modules.talk import Phrase
    from modules.pa import pa
    from modules.PingIPhone import PING
    from modules.control_esp import ESP
    ###############################################################################

    control = ARGUMENTS()
    timing = TIMING() 
    items = OBJECT()
    iPhone = PING()

    for mods in ['GLOBAL','lamp','play','ant']: 
        items.Child(mods,False)
    items.Available()
    
    blinds = True # different logic 
    blinds_on = True  # let them both be true :) 
    logger.info ('started ' + ' '.join(sys.argv) )
    logger.info ('on alarm '.upper() + str(control.alarm))
    logger.info ('on move '.upper() + str(control.move))
    logger.info ('on standby '.upper() + str(control.stb))
    logger.info ('once '.upper() + str(control.once))    
    logger.info ('Fire time: '+ str((timing.fire_time/3600)) + ' hours' )
    Phrase({'TYPE' : 'START_MS'})
#    for k,v in iniFile(os.path.join(self_path,'PINS_ALLOCATION.INI'))['MOVEMENT'].items(): pins[k] = int(v)

    # initial GPIO state
    RELAY_INIT_STATE = 'HIGH' # iniFile(os.path.join(self_path,'PINS_ALLOCATION.INI'))['PARAMETERS']['RELAY_INIT_STATE'] #'HIGH' # HIGH or LOW 
    GPIO_ON = True # compatibility 
    GPIO.INIT = GPIO.HIGH
    GPIO.ON = GPIO.LOW
    GPIO.OFF = GPIO.HIGH

    pins = {'MOVEMENT_SENSOR' : 22, 'BLINK' : 18}
    #%% extra modules 
    def Blink(args = [1,1,0.1]):
        global pins 
        channel = pins['BLINK']
        for b in range(int(args[0])):      
            for a in range(int(args[1])):
                GPIO.output(channel, GPIO.HIGH)	
                sleep(float(args[2]))
                GPIO.output(channel, GPIO.LOW)
                sleep(float(args[2]))
            if int(args[0]) != 1: sleep(0.3)  

    def play(TASK = ['play_current']): 
        wip = kodi('what_is_playing')
        m.log('TASK recieved: ' + TASK[0] + ', wip answer: '+ wip)
        if TASK == ['pause']:
            if wip == 'audio': 
                kodi('pause')
                m.log ('pausing music')
                m.items.play.status = False
            elif wip == 'video':
                m.log ('video is playing. Won\'t stop')
            elif wip == 'nothing': 
                m.log ('nothing is playing')
        else:
            if wip == 'nothing': 
                kodi(TASK[0])
                m.log('starting playing current')
                m.items.play.status = True
            elif wip == 'audio':
                kodi('resume')
                m.log ('resuming audio')
                m.items.play.status = True
            elif wip == 'video':
                m.log('video is current. won\'t do anything')
#%%    
    for k,v in pins.items(): # initiating PINS 
        if k.find('SENSOR') == -1: 
            GPIO.setup(v, GPIO.OUT, initial = GPIO.INIT) 
        else: 
            GPIO.setup(v, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    # ---------------------------------------------------------------- 
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
    
    ##
    def Movement():     
        # for keys within 'm:' section (when iPohne is around)
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

            for mod,arg in getattr(control, category).items(): 
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
#        logger.info( 'no movement for ' + str(int(timing.delay_time)) + ' sec: ,') 
        Movement_by_category(category = 'stb', mod_stat = True)
        items.GLOBAL.status = False
        timing.no_movement_trigger = False
        

    GPIO.add_event_detect(pins['MOVEMENT_SENSOR'], GPIO.RISING, callback=Event, bouncetime=1500) # GPIO.RISING, GPIO.FALLING or GPIO.BOTH.

    # --------------------------------- MAIN LOOP ------------------------------------------------
    while timing.GlobalStop(): 
        iPhone.Ping()
        if iPhone.changed != None: 
            esp = ESP([['1' if i else '0' for i in [iPhone.changed]][0] , '5']) # ESP indicator on 5 esp
            logger.info('iPhone status changed to ' + str(iPhone.changed))
        if iPhone.status == False: 
            ThreadedEvent('Blink 1 1 0.3')
        if timing.count_move == 0: 
            ThreadedEvent('Blink 1 3 0.3')
        if timing.no_movement_trigger:
            #if timing.NoMovement(): # cascade needed to turn trigger once event registered 
            if  iPhone.Status() == False: #  checking considering delay
                logger.info('iPhone - contact lost')
                iPhone_connection_lost()  
        if 'lamp' in control.move.keys(): 
            if timing.TwilightSwitcher('morning') and items.lamp.status:
                logger.info('TwilightSwitcher morning')
                lamp(['OFF'])
                items.lamp.status = False
            # 1 min moment + lamp was OFF + I was around last ... min
            if  timing.TwilightSwitcher('evening') and items.lamp.status == False and iPhone.Status():# timing.IamAround(30): 
                lamp(['ON'])
                timing.Move()
                items.lamp.status = True

				# 		MOVED TO PA-service            
#        # open when morning > opened on move 
#        if timing.TwilightSwitcher('windows_ligth') and blinds_on:
#            log('TwilightSwitcher windows_ligth > blinds close')
#            ESP(['1','123'])
#            blinds_on = False 
        # close on dark 
#        if timing.TwilightSwitcher('total_dark') and blinds:
#            log('TwilightSwitcher total dark > blinds close')
#            ESP(['0','123'])
#            blinds = False 

        sleep(iPhone.Pause([5,45]))  #was 5 - 30 
    
    if ('play' in control.move.keys() or 'play' in control.stb.keys()) and items.play.status: play(['pause'])
    if 'lamp' in control.move.keys(): lamp(['OFF'])
    if datetime.datetime.now().hour >= 20: Phrase({'TYPE' :'GOOD_NIGHT'})
    
    logger.info ('finishing '+ sys.argv[0])
    
    GPIO.cleanup(pins['MOVEMENT_SENSOR'])
    esp = ESP(['0','5'])    
except: 
    Phrase({'TYPE' : 'EXIT_MS'})
    MainException()