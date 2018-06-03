# -*- coding: utf-8 -*-
"""
integration with PA service

Created on Sat Aug 02 08:04:03 2014
@author: ignalex
"""
#DONE: hardcoding out
#DONE: pa vs oct
#DONE: default setup where to run pa
#DONE: pa path OUT
#DONE: pa via ssh or directly
#TODO: whole call to pa via cmd is NOT GOOD

from __future__ import print_function
import __main__ as m

import os,sys
from common import CONFIGURATION, LOGGER

def pa(arg):
    'start PA.py on remote module using ssh'

    config = CONFIGURATION().pa.__dict__
    config['arg'] =  [ arg[0] if type(arg) == list else arg][0]

    if 'ssh' in config.keys():
        cmd = "ssh -p {port} -i {ssh} {user}@{ip} nohup python /home/pi/git/pi/PA.py '{arg}'".format(**config)
    else:
        cmd = "python /home/pi/git/pi/PA.py '{arg}'".format(**config) #was &
    m.logger.info(cmd)
    os.system(cmd)

if __name__ == '__main__':
    logger = LOGGER('pa')
    pa(sys.argv[1:][0]) #pass 1st argument