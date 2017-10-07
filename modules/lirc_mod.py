# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 20:19:13 2015
@author: ignalex
"""

#TODO: fix mapping buttons what do they do
#TODO: integration to new ESP mod via control/rf433/...

from __future__ import print_function

import daemon, sys
from control_esp import ESP #control_esp as ESP
import datetime

def Start():

    XBMC_dic = {'KEY_VOLUMEUP' : 'up',
                'KEY_VOLUMEDOWN' : 'down',
                'KEY_NEXT' : 'next',
                'KEY_PLAY' : 'playpause' ,
                'BOSE_KEY_VOLUMEUP' : 'up',
                'BOSE_KEY_VOLUMEDOWN' : 'down',
                'BOSE_KEY_FORWARD' : 'next',
                'BOSE_KEY_PLAY' : 'resume' ,
                'BOSE_KEY_PAUSE' : 'pause'
                }#,
#           '0' : 'current',
#           '1' : 'current'}
#    extra_kodi_keys = {'9' : 'python /storage/PYTHON/GPIO/modules/ard.py 134-',
#                       '8' : 'python /storage/PYTHON/GPIO/modules/ard.py 134+'}
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
                      'BOSE_BTN_9' : ['6','rf433', 'light', 'on'], 
                      'BOSE_BTN_0' : ['6','rf433', 'light', 'off']
                      }

    last = [None, datetime.datetime.now()]
    while True:
        codeIR = lirc.nextcode()
        if codeIR != []:
            IR = str(codeIR[0])
            log.info( 'code : ' + str(IR))
            if not (IR == last[0] and (datetime.datetime.now() - last[1]).seconds < 1) :  # bouncing
                if IR in XBMC_dic.keys():
                    kodi(XBMC_dic[IR])
#                elif codeIR[0] in extra_kodi_keys.keys():
#                    for com in extra_kodi_keys[codeIR[0]].split(';'):
#                        os.system('ssh -i ~/.ssh/id_rsa root@192.168.1.151 nohup ' + com + ' &')
                elif codeIR[0] in extra_esp_keys:
                    e = ESP()
                    e.Go_parallel(extra_esp_keys[IR])
                else:
                    #TODO: fix talk 
                    log.info('talk is broken for now')
#                    os.system("python /home/pi/git/pi/modules/talk.py " + IR)
            last = [IR, datetime.datetime.now()]
        sleep(0.3)

#TODO: error handling > if error skip 
if __name__ == '__main__':
    with daemon.DaemonContext():
        try:
            from common import LOGGER, PID
            log = LOGGER('lirc')
            logger = log # compatibility
            from time import sleep
            from KODI_control import kodi
            PID()
            import lirc
            sockid = lirc.init("test", blocking = False)
            Start()
        except:
            log.error('error : ' + str(sys.exc_info()))