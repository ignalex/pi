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
#DONE: option > send command to SERVICE by PORT
#TODO: handling : and a_1:a_2 syntax \

from __future__ import print_function
import __main__ as m

import os,sys
from common import CONFIGURATION, LOGGER

def pa(args):
    """
    wrapper pa for many
    pa([run1_options1:run2_options2])
    """

    if args[0].find(':') == -1: #  one
        _pa(args)
    else:
        for n, job in enumerate(args[0].split(':')):
            m.logger.debug(str(n) +  ' : ' + str(job))
            _pa(job.slpit('_'))


def _pa(args):
    "subtask pa"
    """call common PA methods via api or local or on remote using ssh
    - pa = direct|yes
    - pa = ip|192.168.1.154,user|pi,ssh|/home/pi/.ssh/octopus,port|2227
    - pa = api|,host|localhost,port|8083
    pa([RUN,{options}])
    """

    config = CONFIGURATION().pa.__dict__
    config['RUN'] = args[0].upper() if type(args) == list else args.upper() # 1st param is MODULE

    if 'ssh' in config.keys():
        cmd = "ssh -p {port} -i {ssh} {user}@{ip} nohup python /home/pi/git/pi/PA.py '{RUN}'".format(**config)
    elif 'api' in config.keys():
        config['params'] = '' if len(args) == 1 else '\&args='+';'.join(args[1:])
        cmd = "curl {host}:{port}/cmnd?RUN={RUN}{params}".format(**config)
    else:
        cmd = "python3 /home/pi/git/pi/PA.py '{RUN}'".format(**config) #was &
    m.logger.info(cmd)
    os.system(cmd)

if __name__ == '__main__':
    logger = LOGGER('pa')
    pa([i for i in sys.argv[1:] if i != '-d']) #pass args as list