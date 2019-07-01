#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 10:54:50 2019

PURPOSE: 
    - based on the solar kW generated, remote control power consumption
    - built for GB

@author: AI.
"""

from __future__ import print_function

from modules.common import  LOGGER, CONFIGURATION, MainException#, Dirs
from modules.rf433 import rf433
from modules.dht11 import dht11
from modules.rgb_led import color
from modules.sevensegments import sevensegments 


def solar_logic():
    "main module"


if __name__ == '__main__':
    logger = LOGGER('solar', level = 'INFO')
    p = CONFIGURATION()
    
    try:
        #TODO: do we need daemon if planning to use is as a service?
        import daemon
        with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
            solar_logic()
    except:
        MainException()    