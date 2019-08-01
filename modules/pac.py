# -*- coding: utf-8 -*-
"""
integration with PA service

Created on Sat Aug 02 08:04:03 2014
@author: ignalex
"""

from __future__ import print_function
import __main__ as m

import os,sys
from common import LOGGER

def pac(*args, **kargs):
    "python pac.py TIME HR"
    cmd = "curl localhost:8083/cmnd?RUN={}".format(args[0]) +  ('' if len(args) == 1 else '\&args='+';'.join(args[1:]))
    m.logger.info(cmd)
    os.system(cmd)

if __name__ == '__main__':
    logger = LOGGER('pac')
    pac(sys.argv[1:])
