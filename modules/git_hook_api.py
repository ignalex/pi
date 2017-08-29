# -*- coding: utf-8 -*-
"""
server listenning to GIT hook command to pull the master

Created on Wed Aug 30 08:35:00 2017
@author: ignalex
"""
from __future__ import print_function
from flask import Flask
from common import LOGGER # Dirs, CONFIGURATION, MainException,

logger = LOGGER('git_hook')
app = Flask(__name__)

@app.route("/test")
def test():
    global logger 
    logger.info('test')
    

if __name__ == '__main__' : 
    app.run(debug=False, use_debugger = False, use_reloader = False, port = 8081, host = '0.0.0.0')
