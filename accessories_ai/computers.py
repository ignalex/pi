# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 19:15:48 2018

@author: Alexander Ignatov
"""

import requests
import sys
sys.path.append('/home/pi/git/pi/modules') #!!!: out
import logging
logger = logging.getLogger(__name__)
from talk import Speak
from PingIPhone import PingIP #can ping names


from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SWITCH
from time import sleep
import os
import datetime

class SYSTEM(Accessory):
    category = CATEGORY_SWITCH

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        serv = self.add_preload_service('Switch', chars=['On','Name'])
        self.char_on = serv.configure_char(
            'On', setter_callback=self.OnOff)
        self.char_name = serv.configure_char('Name')
        self.char_name.value = args[1]
        self.id = args[1]
        self.__last_call__ = [datetime.datetime.now() - datetime.timedelta(hours=1)]

    def __setstate__(self, state):
        self.__dict__.update(state)

    def OnOff(self, value):
        logger.info('{} on / off: {}'.format(self.id, value))
        if value:
#            globals()['_' + self.id + '_on']
            getattr(self,'_' + self.id + '_on')()
            self.char_on.value = 1
            self.char_on.notify()
            logger.info(self.id + ' turned ON')

        else:
            if (datetime.datetime.now() - self.__last_call__[-1]).seconds < 60:
#                globals()['_' + self.id + '_off']
                getattr(self,'_' + self.id + '_off')()
                self.char_on.value = 0
                self.char_on.notify()
                logger.info(self.id + ' turned OFF')
            else:
                logger.debug('more than 60 sec from last call > need the second command')
            self.__last_call__.append(datetime.datetime.now())

    @Accessory.run_at_interval(60)
    def run(self):
#        globals()['_run_at_interval_' + self.id](self)
        if hasattr(self,  '_run_at_interval_' + self.id):
            getattr(self, '_run_at_interval_' + self.id)()

    def stop(self):
        super().stop()


    #%% specific
    def _hippopotamus_on(self):
        os.system('python /home/pi/git/pi/modules/wol.py hippo')

    def _hippopotamus_off(self):
        os.system('/usr/bin/ssh -i /home/pi/.ssh/hippopotamus ai@hippo.local sudo poweroff')

    def _raid_on(self):
        return requests.request('GET', 'http://192.168.1.175/control/pin/14/1', timeout = 1).ok

    def _raid_off(self):
        return requests.request('GET', 'http://192.168.1.175/control/pin/14/0', timeout = 1).ok

    def _run_at_interval_raid(self):
        "scanning and propogating state"

        logger.debug('requesting raid status')
        com = 'http://192.168.1.175/control/rf_states'
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

    def _run_at_interval_hippopotamus(self):
        logger.debug('requesting hippo status')
        status = int(PingIP('hippo.local')[0])
        if self.char_on.value != int(status): #status changed outside
            logger.info('state for {} changed to {}'.format(self.id, status))
            Speak('state for {} changed to {}'.format(self.id, status))
            self.char_on.value = status
            self.char_on.notify()