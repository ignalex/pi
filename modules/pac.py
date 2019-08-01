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

def pac(run, args=None):
    "python pac.py time hr"
    cmd = "curl localhost:8083/cmnd?RUN={}".format(run) +  ('' if args is None else '\&args='+args)
    m.logger.info(cmd)
    os.system(cmd)

if __name__ == '__main__':
    logger = LOGGER('pac')
    if len(sys.argv) == 1:
        pac(sys.argv[1])
    else:
        pac(sys.argv[1], sys.argv[2])