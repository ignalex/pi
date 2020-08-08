# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 07:57:18 2018

@author: Alexander Ignatov
"""
import sys
from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR
import requests
sys.path.append('/home/pi/git/pi/modules')

from temperature import Temp
import logging
logger = logging.getLogger(__name__)

import __main__ as m

class TemperatureSensor(Accessory):
    category = CATEGORY_SENSOR
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    @Accessory.run_at_interval(60)
    def run(self):
        self.char_temp.set_value(Temp())


class LightSensor(Accessory):
    category = CATEGORY_SENSOR
    def __init__(self, *args, ip='192.168.1.176', **kwargs):
        super().__init__(*args, **kwargs)

        serv_light = self.add_preload_service('LightSensor', chars=['CurrentAmbientLightLevel','Name'])
        self.char_lux = serv_light.configure_char('CurrentAmbientLightLevel')
        self.name = serv_light.configure_char('Name')
        self.name.set_value({'192.168.1.175':'North', '192.168.1.176':'East'}[ip])
        self.ip = ip
        self.id = 'sensor'

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
        com = 'http://{}/control/sensor'.format(self.ip)
        try:
            light = int(requests.request('GET', com, timeout = 5).json()['data']['sensor'])
        except:
            light = 0 # if none > returns error 'non numeric'
        logger.info('light on {} = {}'.format(self.ip.split('.')[-1], str(light)))
        return light

        # if self.id not in m.st.status.keys():
        #     logger.debug('status for {} is not set'.format(self.id))
        #     return 0
        # else :
        #     logger.info('light on {} = {}'.format(self.ip.split('.')[-1], str(m.st.status[self.id])))
        #     return int(m.st.status[self.id])

# class InternetSpeed(Accessory):
#     category = CATEGORY_SENSOR
#     def __init__(self, *args, task='download', **kwargs):
#         super().__init__(*args, **kwargs)
#         self.task = task
#         serv = self.add_preload_service('LightSensor')
#         self.char = serv.configure_char('CurrentAmbientLightLevel') #TODO: change type / change units

#     @Accessory.run_at_interval(60 * 10) # 10 min
#     def run(self):
#         self.char.set_value(self.speed())

#     def speed(self, value=''):
#         com = 'http://192.168.1.155:8082/internet_speed_simple'
#         resp = requests.request('GET', com, timeout = 5).json()[self.task]
#         logger.info('internet speed > ' + str(resp))
#         return resp

