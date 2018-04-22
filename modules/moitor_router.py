#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 07:14:48 2018

@author: s84004
"""

from __future__ import print_function
import __main__ as m
import os
from time import sleep

from common import  LOGGER
from PingIPhone import PingIP

def RebootOnLostConnection():
    "reboot pi on loosing connection to router"
    for attempt in range(0,5):
        if PingIP(1)[0] == False:
            m.logger.info('no connection found, attempt ' + str(attempt))
        else:
            m.logger.debug('router ping : OK')
            return
        sleep(60)
    m.logger.error('REBOOTING PI')
    os.system('sudo reboot')

if __name__ == '__main__':
    logger = LOGGER('RebootOnLostConnection')
    RebootOnLostConnection()