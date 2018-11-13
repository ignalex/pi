# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 07:57:18 2018

@author: Alexander Ignatov
"""
import sys
sys.path.append('/home/pi/git')

from HAP.pyhap.accessory import Accessory
from HAP.pyhap.const import CATEGORY_WINDOW_COVERING,CATEGORY_WINDOW
import requests
from time import sleep
sys.path.append('/home/pi/git/pi/modules')
import logging
logger = logging.getLogger(__name__)



class WindowCovering(Accessory):
#    category = CATEGORY_WINDOW
    category = CATEGORY_WINDOW_COVERING

    def __init__(self, *args, ip=175, **kwargs):
        super().__init__(*args, **kwargs)

#        serv_window = self.add_preload_service('Window', chars=['CurrentPosition','TargetPosition','PositionState','Name'])
        serv_window = self.add_preload_service('WindowCovering', chars=['CurrentPosition','TargetPosition','PositionState','Name'])
        self.char_current_pos = serv_window.configure_char(
            'CurrentPosition')# value = 0 maxValue = 100
        self.char_target_pos = serv_window.configure_char(
            'TargetPosition', setter_callback=self.target_position)# value = 0 maxValue = 100
        self.char_pos_state = serv_window.configure_char('PositionState')       # validValues = [0, 1, 2] ([decreasing, increasing, stopped])

        self.name = serv_window.configure_char('Name')
        self.name.set_value({175:'North window', 176:'East window'}[ip])
        self.ip = ip

    def __getstate__(self):
        state = super().__getstate__()
#        state["window"] = None
        logger.debug(str(state))
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def target_position(self, value):

        if value == 0:
            direction = 0
        elif value == 100:
            direction = 1
        else:
            logger.error('currently support ALL open / close')
            return
        logger.info('receiced: ' + str(value) + ', direction:' + str(direction))

        steps = 2000

        self.char_pos_state.set_value(direction)

        com = 'http://192.168.1.{}/control/motor/{}/{}'.format(self.ip, direction, steps)
        resp = requests.request('GET', com, timeout = 10).json()['data'] # here prob waiting for finishing
        logger.info(str(resp))

        self.char_pos_state.set_value(2)
        logger.info('states set, finished')
