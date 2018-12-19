# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 07:57:18 2018

@author: Alexander Ignatov
"""
import sys
from HAP.pyhap.accessory import Accessory
from HAP.pyhap.const import CATEGORY_SENSOR
import requests
sys.path.append('/home/pi/git/pi/modules')
sys.path.append('/home/pi/git')

from temperature import Temp
import logging
logger = logging.getLogger(__name__)


class TemperatureSensor(Accessory):

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    @Accessory.run_at_interval(5)
    def run(self):
        self.char_temp.set_value(Temp())


class LightSensor(Accessory):
    category = CATEGORY_SENSOR

    def __init__(self, *args, ip=175, **kwargs):
        super().__init__(*args, **kwargs)

        serv_light = self.add_preload_service('LightSensor', chars=['CurrentAmbientLightLevel','Name'])
        self.char_lux = serv_light.configure_char('CurrentAmbientLightLevel')
        self.name = serv_light.configure_char('Name')
        self.name.set_value({175:'North', 176:'East'}[ip])
        self.ip = ip

    def __getstate__(self):
        state = super().__getstate__()
        state["light"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.light = self.getreadings()

    @Accessory.run_at_interval(60)
    def run(self):
        self.char_lux.set_value(self.getreadings())

    def getreadings(self):
        com = 'http://192.168.1.{}/control/sensor'.format(self.ip)
        try:
            light = int(requests.request('GET', com, timeout = 5).json()['data']['sensor'])
        except:
            light = 0 # if none > returns error 'non numeric'
        logger.info('light on {} = {}'.format(self.ip, str(light)))
        return light



