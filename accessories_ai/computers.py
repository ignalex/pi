# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 19:15:48 2018

@author: Alexander Ignatov
"""

#import requests
import sys
sys.path.append('/home/pi/git/pi/modules') #!!!: out
import logging
logger = logging.getLogger(__name__)
from talk import Speak
from PingIPhone import PingIP #can ping names


from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SWITCH
#from time import sleep
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
            getattr(self,'_' + self.id + '_on')()
            self.char_on.value = 1
            self.char_on.notify()
            logger.info(self.id + ' turned ON')

        else:
            if (datetime.datetime.now() - self.__last_call__[-1]).seconds < 60:
                getattr(self,'_' + self.id + '_off')()
                self.char_on.value = 0
                self.char_on.notify()
                logger.info(self.id + ' turned OFF')
            else:
                logger.debug('more than 60 sec from last call > need the second command')
            self.__last_call__.append(datetime.datetime.now())

    @Accessory.run_at_interval(60)
    def run(self):
        if hasattr(self,  '_run_at_interval'):
            getattr(self, '_run_at_interval')()

    def stop(self):
        super().stop()

    #%% specific
    def _hippo_on(self):
        os.system('python /home/pi/git/pi/modules/wol.py {}'.format(self.id))

    def _hippo_off(self):
        os.system('/usr/bin/ssh -i /home/pi/.ssh/hippo ai@hippo.local sudo poweroff')

    def _rhino_on(self):
        os.system('python /home/pi/git/pi/modules/wol.py {}'.format(self.id))

    def _rhino_off(self):
        "not implemented yet"
        logger.info('_rhino_off : not implemented yet')


    def _run_at_interval(self):
        logger.debug('requesting {} status'.format(self.id))
        status = int(PingIP('{}.local'.format(self.id))[0])

        if self.char_on.value != int(status): #status changed outside
            logger.info('{} is {}'.format(self.id, 'on' if status else 'off'))
            Speak('{} is {}'.format(self.id, 'on' if status else 'off'))
            self.char_on.value = status
            self.char_on.notify()