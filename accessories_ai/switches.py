# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 19:15:48 2018

@author: Alexander Ignatov
"""
#TODO: add power outlet
#TODO: find button event

import requests
import sys
sys.path.append('/home/pi/git/pi/modules') #!!!: out
#from functools import partial
import logging
logger = logging.getLogger(__name__)
from talk import Speak

from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_LIGHTBULB, CATEGORY_SWITCH, CATEGORY_PROGRAMMABLE_SWITCH
from time import sleep
import os
import datetime

class AllSwitches(Accessory):
    category = CATEGORY_LIGHTBULB #???: how affects?

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.service = {'light' : ['Lightbulb', 'set_switch'],
                        'heater': ['Switch', 'set_switch'],
                        'coffee': ['Switch', 'set_switch'],
                        '13':     ['Switch', 'set_switch'],
                        'beep' :  ['Switch', 'beep'],
                        'watering' : ['Switch', 'watering'],
                        'hippopotamus' : ['Switch', 'hippopotamus']
                        }[args[1]]
        serv = self.add_preload_service(self.service[0], chars=['On','Name'])
        self.char_on = serv.configure_char(
            'On', setter_callback=getattr(self, self.service[1]))
        self.id = args[1]
        self.char_name = serv.configure_char('Name')
        self.char_name.value = self.id

    def __setstate__(self, state):
        self.__dict__.update(state)

    def set_switch(self, value):
        com = 'http://192.168.1.176/control/rf433/{}/{}'.format(self.id, value)
        resp = requests.request('GET', com, timeout = 5).json()['data']
        logger.info(str(resp))

    def beep(self, value):
        com = 'http://192.168.1.176/control/beep/{}' #testing
        logger.info('BEEP: value {}'.format(value))
        if not value: return

        for a in range(0,value):
            resp = requests.request('GET', com.format(1), timeout = 5).json()['data']
            sleep(0.2)
            resp = requests.request('GET', com.format(0), timeout = 5).json()['data']
            logger.info(str(resp))

        self.char_on.value = 0
        self.char_on.notify()

    def watering(self, value):
        logger.info('watering: value {}'.format(value))
        if not value: return
        os.system('python /home/pi/git/pi/watering.py water_hap')
        self.char_on.value = 0
        self.char_on.notify()

    def hippopotamus(self, value):
        #need a safety switch > not to turn off by mistake.
        if not hasattr(self, '__last_call__'): self.__last_call__ = [datetime.datetime.now() - datetime.timedelta(hours=1)]
        logger.info('hippo on / off: {}'.format(value))
        if value: #on
            os.system('python /home/pi/git/pi/modules/wol.py HIPPO')
            logger.info('turned ON')
            self.char_on.value = 1
            self.char_on.notify()
        else:
            # off only if 2 calls to off within 10 sec
            if (datetime.datetime.now() - self.__last_call__[-1]).seconds < 10:
                os.system('/usr/bin/ssh -i /home/pi/.ssh/hippo ai@hippo.local sudo poweroff')
                logger.info('turned OFF')
                self.char_on.value = 0
                self.char_on.notify()
            else:
                logger.debug('more than 10 sec from last call > need second command')
                self.__last_call__.append(datetime.datetime.now())


    @Accessory.run_at_interval(30) #!!!: errors but work with naming 'run'
    def run(self):
        "scanning and propogating state"
        if self.id not in ['light', 'coffee', 'heater']: return #TODO: make sure it is not pinging watering or beep
        logger.debug('requesting status for {}'.format(self.id))
        com = 'http://192.168.1.176/control/rf_states'
        for attempt in range(0,2):
            try:
                resp = requests.request('GET', com, timeout = 1)#.json()['data']['rf_states']
                if resp.ok:
                    j = resp.json()['data']['rf_states']
                    if self.id in j.keys():
                        if self.char_on.value != int(j[self.id]): #status changed outside
                            logger.info('state for {} changed to {}'.format(self.id, int(j[self.id])))
                            Speak('state for {} changed to {}'.format(self.id, int(j[self.id]))) #!!!: remove later
                            self.char_on.value = int(j[self.id])
                            self.char_on.notify()
                    else:
                        logger.debug('no rf_state for {} returned'.format(self.id))
                    return
                else:
                    sleep(0.2)
            except Exception as e:
                logger.error('cant get meaningful response from ESP {} - attempt {}: {}'.format(self.id, attempt, str(e)))

    def stop(self):
        super().stop()

class ProgramableSwitch(Accessory):
    #TODO: doesn't work
    """ "StatelessProgrammableSwitch": {
      "OptionalCharacteristics": [
         "Name",
         "ServiceLabelIndex"
      ],
      "RequiredCharacteristics": [
         "ProgrammableSwitchEvent"
      ],"""
    category = CATEGORY_PROGRAMMABLE_SWITCH

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.service = {'program 1' : ['StatelessProgrammableSwitch', 'ProgrammableSwitchEvent']
                        }['program 1']
        serv = self.add_preload_service(self.service[0])
        self.char = serv.configure_char(self.service[1])#, setter_callback=getattr(self, args[1]))

    def __setstate__(self, state):
        self.__dict__.update(state)

    def stop(self):
        super().stop()

# !!!: for future
#def add_methods(obj, funcs):
#        'Binding extra methods and store it in an object. funcs = [f1, f2] '
#        logger.debug('adding methods ' )#+ str(funcs))
#        for func in funcs:
#            setattr(obj, func.__name__, partial( func, obj))