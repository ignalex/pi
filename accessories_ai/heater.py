# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 19:15:48 2018

@author: Alexander Ignatov
"""

# An Accessory for a LED attached to pin 11.
import requests
import sys
sys.path.append('/home/pi/git/pi/modules')
from common import LOGGER

from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_THERMOSTAT

logger = LOGGER('HAP_heater', 'INFO')

class Heater(Accessory):

    category = CATEGORY_THERMOSTAT

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        serv_light = self.add_preload_service('Switch')
        self.char_on = serv_light.configure_char(
            'On', setter_callback=self.set_heater)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def set_heater(self, value):
        com = 'http://192.168.1.176/control/rf433/heater/{}'.format(value)

        resp = requests.request('GET', com, timeout = 4).content.replace(b'<!DOCTYPE HTML>\r\n<html>\r\n', b'').replace(b'</html>\n',b'')
        logger.info(str(resp))

    def stop(self):
        super().stop()
