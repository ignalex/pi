# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 19:15:48 2018

@author: Alexander Ignatov
"""
#TODO: add power outlet
#TODO: find button event

import requests
import sys
import threading

sys.path.append('/home/pi/git/pi/modules') #!!!: out
#from functools import partial
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")

try:
    from talk import Speak
except:
    pass

from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_LIGHTBULB, CATEGORY_SWITCH, CATEGORY_PROGRAMMABLE_SWITCH
from time import sleep
import os
import datetime

import __main__ as m

#%%
class AllSwitches(Accessory):
    category = CATEGORY_LIGHTBULB #???: how affects?

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.id = args[1]
        self.service = {'light' :       ['Lightbulb', 'set_switch_esp'],
                        'heater':       ['Switch', 'set_switch_esp'],
                        'coffee':       ['Switch', 'set_switch_esp'],
                        'ambient_light':['Switch', 'set_switch_sonoff', {'IP': '192.168.1.18'}],
                        'beep' :        ['Switch', 'beep'],
                        'watering' :    ['Switch', 'watering']
                        }[self.id]
        serv = self.add_preload_service(self.service[0], chars=['On','Name'])
        self.char_on = serv.configure_char(
            'On', setter_callback=getattr(self, self.service[1]))
        # switch_type : sonoff or esp or None
        self.switch_type = self.service[1].split('_')[2] if self.service[1].find('set_switch') != -1 else None
        # extra config / IP etc
        self.metadata = self.service[2]  if len(self.service) > 2 else None
        self.char_name = serv.configure_char('Name')
        self.char_name.value = self.id

    def __setstate__(self, state):
        self.__dict__.update(state)

    def set_switch_esp(self, value):
        com = 'http://192.168.1.176/control/rf433/{}/{}'.format(self.id, value)
        resp = requests.request('GET', com, timeout = 5).json()['data']
        logger.info(str(resp))

    def set_switch_sonoff(self, value):
        com = 'http://{}/cm?cmnd=Power%20{}'.format(self.metadata['IP'], value)
        #http://<ip>/cm?cmnd=Power%20On
        #PowerOnState
        resp = requests.request('GET', com, timeout = 5).content
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

    @Accessory.run_at_interval(60)
    def run(self):
        "!! status collector must be called from main module first with name st"
        logger.debug('requesting status for {}'.format(self.id))

        if  self.switch_type in ['esp',None]:
            if self.id not in m.st.status.keys():
                logger.debug('status for {} is not set'.format(self.id))
                return
            if self.char_on.value != int(m.st.status[self.id]): #status changed outside
                logger.info('state for {} changed to {}'.format(self.id, m.st.status[self.id]))
               # Speak('state for {} changed to {}'.format(self.id, int(m.st.status[self.id])))
                self.char_on.value = int(m.st.status[self.id])
                self.char_on.notify()
        elif self.switch_type == 'sonoff':
            com = 'http://{}/cm?cmnd=Power'.format(self.metadata['IP'])
            resp = requests.request('GET', com, timeout = 5).json()['POWER']
            logger.info(str(resp)) #!!!: parse response + pass to accessory
            self.char_on.value = 1 if resp == 'ON' else 0
            self.char_on.notify()

    def stop(self):
        super().stop()

#class ProgramableSwitch(Accessory):
#    #???: doesn't work
#    """ "StatelessProgrammableSwitch": {
#      "OptionalCharacteristics": [
#         "Name",
#         "ServiceLabelIndex"
#      ],
#      "RequiredCharacteristics": [
#         "ProgrammableSwitchEvent"
#      ],"""
#    category = CATEGORY_PROGRAMMABLE_SWITCH
#
#    def __init__(self, *args,  **kwargs):
#        super().__init__(*args, **kwargs)
#        self.service = {'program 1' : ['StatelessProgrammableSwitch', 'ProgrammableSwitchEvent']
#                        }['program 1']
#        serv = self.add_preload_service(self.service[0])
#        self.char = serv.configure_char(self.service[1])#, setter_callback=getattr(self, args[1]))
#
#    def __setstate__(self, state):
#        self.__dict__.update(state)
#
#    def stop(self):
#        super().stop()
#%%
class EspStatusCollector(): #TODO: collector for SONOFF
    " status collector? >>> one pre-stored element"
    " get into threading"
    def __init__(self, ips = [175, 176]):
        self.ips =          ips
        self.DO =           True
        self.sleep =        60 # seconds
        self.status =       {} # falettening structure : keys must be unique
        self.online =       {i : {} for i in ips}
        self.last_update =  {i : None for i in ips}
        self.config =       dict(attempts=2, timeout=2, interval=60)
        self.Start()

    def Start(self):
        threading.Thread(target=self.Update).start()

    def Stop(self):
        logger.info('status collection : STOPPING')
        self.DO = False

    def Update(self):
        "for all IPs "
        while True:
            last = datetime.datetime.now()
            for ip in self.ips: self.Check(ip)
            while datetime.datetime.now() < last + datetime.timedelta(seconds = self.sleep):
                sleep(1)
                if not self.DO:
                    logger.info('Status collector finished')
                    return

    def Check(self, ip=176):
        "checking status per IP and setting json element of status all"
        logger.debug('requesting status on {}'.format(ip))
        com = 'http://192.168.1.{}/control/rf_states'.format(ip)
        for attempt in range(0, self.config['attempts']):
            try:
                logger.debug('{} {}'.format(ip, attempt) )
                resp = requests.request('GET', com, timeout = self.config['timeout'])
                logger.debug(str(resp.content))
                if resp.ok:
                    for k, v in resp.json()['data']['rf_states'].items():
                        self.status[k] = v
                    self.online[ip] = True
                    self.last_update[ip] = datetime.datetime.now()
                    logger.debug('{} OK'.format(ip) )
                    return True
                else:
                    sleep(0.2)
            except Exception as e:
                logger.error('cant get meaningful response from ESP {} - attempt {}: {}'.format(ip, attempt, str(e)))
        self.online[ip] = False
        return False # after N attempts can't get reply

