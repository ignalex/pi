# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 06:41:02 2018

@author: Alexander Ignatov
"""
import sys
sys.path.append('/home/pi/git/pi/modules')
from common import LOGGER
import time

if __name__ == '__main__':
    logger = LOGGER('service_test', 'INFO')
    while True:
        logger.info('service ping ')
        time.sleep(10)