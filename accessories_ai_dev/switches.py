# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 19:15:48 2018

@author: Alexander Ignatov
"""

# An Accessory for a LED attached to pin 11.
import requests
import sys
sys.path.append('/home/pi/git/pi/modules')
sys.path.append('/home/pi/git')

import logging
logger = logging.getLogger(__name__)

from HAP.pyhap.accessory import Accessory
from HAP.pyhap.const import CATEGORY_LIGHTBULB, CATEGORY_SWITCH


class AllSwitches(Accessory):
    category = CATEGORY_LIGHTBULB

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.service = {'light' : ['Lightbulb', 'light'],
                        'heater': ['Switch', 'heater'],
                        'coffee': ['Switch', 'coffee']
                        }[args[1]]
        serv = self.add_preload_service(self.service[0])
        self.char_on = serv.configure_char(
            'On', setter_callback=self.set_switch)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def set_switch(self, value):
        com = 'http://192.168.1.176/control/rf433/{}/{}'.format(self.service[1], value)
        resp = requests.request('GET', com, timeout = 5).json()['data']
        logger.info(str(resp))

    def stop(self):
        super().stop()