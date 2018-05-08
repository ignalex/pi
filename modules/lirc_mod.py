# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 20:19:13 2015
@author: ignalex
"""

#DONE: fix mapping buttons what do they do
#DONE: integration to new ESP mod via control/rf433/...
#DONE: light on / off
#DONE:  dim ON / off
#DONE: error handling > if error skip
#TODO: add all coded keys > with nothing mapped.

from __future__ import print_function

#import daemon
from control_esp import ESP #control_esp as ESP
from talk import Speak
import datetime, sys

def Start():
    logger.debug('entered START')
    XBMC_dic = {'KEY_VOLUMEUP' : 'up',
                'KEY_VOLUMEDOWN' : 'down',
                'KEY_NEXT' : 'next',
                'KEY_PLAY' : 'playpause' ,
                'BOSE_KEY_VOLUMEUP' : 'up',
                'BOSE_KEY_VOLUMEDOWN' : 'down',
                'BOSE_KEY_FORWARD' : 'next',
                'BOSE_KEY_PLAY' : 'resume' ,
                'BOSE_KEY_PAUSE' : 'pause'
                }
    extra_esp_keys = {'minus' : ['0','123'],
                      'plus' : ['1', '123'],
                      '1' : ['1', '1'],
                      '2' : ['1','23'],
                      '3' : ['1','123'],
                      '4' : ['0', '1'],
                      '5' : ['0','23'],
                      '6' : ['0','123'],
                      'BOSE_BTN_1' : ['1', '1'],
                      'BOSE_BTN_2' : ['1','23'],
                      'BOSE_BTN_3' : ['1','123'],
                      'BOSE_BTN_4' : ['0', '1'],
                      'BOSE_BTN_5' : ['0','23'],
                      'BOSE_BTN_6' : ['0','123'],
                      'BOSE_BTN_7' : ['6','rf433', 'dimlight', 'on'],
                      'BOSE_BTN_8' : ['6','rf433', 'dimlight', 'off'],
                      'BOSE_BTN_9' : ['6','rf433', 'light', 'on'],
                      'BOSE_BTN_0' : ['6','rf433', 'light', 'off']
                      }
    last = [None, datetime.datetime.now()]
    while True:
        try:
            codeIR = lirc.nextcode()
            if codeIR != []:
                IR = str(codeIR[0])
                logger.info( 'code : ' + str(IR))
                if not (IR == last[0] and (datetime.datetime.now() - last[1]).seconds < 1) :  # bouncing
                    if IR in XBMC_dic.keys():
                        kodi(XBMC_dic[IR])
                    elif codeIR[0] in extra_esp_keys:
                        e = ESP()
                        e.Go_parallel(extra_esp_keys[IR])
                    else:
                        logger.info('speaking only ' + IR)
                        Speak(IR)
                last = [IR, datetime.datetime.now()]
        except:
            logger.error('error : ' + str(sys.exc_info()))
            Speak('error in lirc module')
            sleep (2)
        sleep(0.3)

if __name__ == '__main__':
#    with daemon.DaemonContext():
        try:
            from common import LOGGER, PID
            logger = LOGGER('lirc')
#            logger = log # compatibility
            logger.info('starting lirc')
            from time import sleep
            from KODI_control import kodi
            PID()
            import lirc
            sockid = lirc.init("test", blocking = False)
            Start()
        except:
            logger.error('error on initiation: ' + str(sys.exc_info()))