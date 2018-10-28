# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 07:57:18 2018
@author: Alexander Ignatov

using esp8266 as a NEMA motor controller controlled over wifi
code at https://github.com/ignalex/esp.git

"""
#TODO: generic IP instead of 192.168.1.xxx

#import sys

from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_WINDOW_COVERING
import requests
import sys
sys.path.append('/home/pi/git/pi/')
import logging
logger = logging.getLogger(__name__)
from talk import Speak

class WindowCovering(Accessory):

    category = CATEGORY_WINDOW_COVERING

    def __init__(self, *args, ip=175, calibrate=True, speak=None, minStep=10, **kwargs):
        super().__init__(*args, **kwargs)

        serv_window = self.add_preload_service('WindowCovering',
                        chars=['CurrentPosition','TargetPosition',
                               'PositionState','Name', 'ObstructionDetected'])
        self.char_current_pos = serv_window.configure_char('CurrentPosition')# value = 0 maxValue = 100
        self.char_target_pos = serv_window.configure_char('TargetPosition',
                                        setter_callback=self.target_position)# value = 0 maxValue = 100
        self.char_pos_state = serv_window.configure_char('PositionState')       # validValues = [0, 1, 2] ([decreasing, increasing, stopped])
        self.char_obstraction = serv_window.configure_char('ObstructionDetected')       # validValues = [0, 1, 2] ([decreasing, increasing, stopped])

        self.name = serv_window.configure_char('Name')
        self.name.set_value({175:'North window', 176:'East window'}[ip])
        self.ip = ip
        self.speak = speak
        # steps per percent opening - depends on length. and delay - speed.
        self.steps_config = {'delay' : 11,
                             'multi' : {175 : 30, 176 : 100}[ip],
                             'timeout' : 20, 'calibrate_position' : 100,
                             'use_hcsr_when_down_always' : False,
                             'skip_steps' : 50 } # every N steps one scan for hcsr [only when hcsr enabled - at calibrate]
        self.char_target_pos.properties['minStep'] = minStep

        if calibrate: self.calibrate()

    def calibrate(self):
        'UpDown 0 - leave closed, 100 - leave opened'
        self.calibrated = None
        logger.info('window on {} initiated > calibration'.format(self.ip))
        if self.speak:
            Speak('calibrating window')
        self.target_position(0,calibrate=True)
        self.calibrated = True
        if self.steps_config['calibrate_position'] > 0:
#            if self.speak:
#                Speak('openning up'.format(self.steps_config['calibrate_position']))
            self.char_target_pos.set_value(self.steps_config['calibrate_position']) # no trigger yet
            self.target_position(self.steps_config['calibrate_position'])

    def __getstate__(self):
        state = super().__getstate__()
#        state["window"] = None
        logger.debug(str(state))
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def target_position(self, value, calibrate=False):
        """delta between current and target
        : for calibration target = 0, current = 100. hcsr MUST be on (!)
        """
        target = value
        current = self.char_current_pos.get_value()

        if calibrate: current = 100 # override
        delta = target - current
        if delta == 0 :
            logger.debug('delta is 0 : no changes')
            return
        direction = int(delta > 0)
        steps = delta * self.steps_config['multi']

        logger.info('motor {}: current {}, target {}, delta {}, direction {}, steps {}, use hcsr {}'.\
                    format(self.ip, target, current, delta, direction, steps, self.steps_config['use_hcsr_when_down_always']))

        self.char_pos_state.set_value(direction)

        com = 'http://192.168.1.{}/control/motor/{}/{}/{}/{}'.\
                format(self.ip,
                       steps,
                       self.steps_config['delay'],
                       int(self.steps_config['use_hcsr_when_down_always'] or calibrate),
                       self.steps_config['skip_steps'])
        try:
            resp = requests.request('GET', com, timeout = self.steps_config['timeout']).json()['data'] # here prob waiting for finishing
            logger.info(str(resp))
            # obstraction
            if resp['motor']['status'] == False:
                self.char_obstraction.set_value(True)
                logger.error('obstraction detected')
            elif resp['motor']['status'] == True:
                self.char_obstraction.set_value(False) # reseting
        except Exception as e:
            # nothing returned
            self.char_obstraction.set_value(True)
            logger.error('wrong answer from ESP > obstraction detected')
            logger.error(str(e))

        try:
            self.char_current_pos.set_value(value) ## test here
        except Exception as e:
            logger.error(str(e))

        self.char_pos_state.set_value(2)

        logger.debug('states set. target {}, current {}, posState {}'.format(
                self.char_target_pos.get_value(),
                self.char_current_pos.get_value(),
                self.char_pos_state.get_value()))

