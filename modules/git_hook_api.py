# -*- coding: utf-8 -*-
"""
server listenning to GIT hook command to pull the master

Created on Wed Aug 30 08:35:00 2017
@author: ignalex
"""
from __future__ import print_function
from flask import Flask, request
from common import LOGGER, Dirs #, CONFIGURATION, MainException,
from subprocess import Popen, PIPE
import daemon

logger = LOGGER('git_hook')
app = Flask(__name__)

@app.route("/test")
def test():
    global logger 
    logger.info('test')
    return 'test'
    
#TODO: secure / paiload 
#TODO: speak on update 
#TODO: email feedback > after secured config     
@app.route("/git_pull", methods=['POST'])
def git_pull():
    global logger 
    logger.info('JSON payload' + str(request.json))
    process = Popen('git pull'.split(' '), stdout=PIPE, stderr=PIPE, cwd=Dirs()['REPO'])
    reply  = ' : '.join([str(i) for i in process.communicate() ]) 
    logger.info(reply)
    return reply 

if __name__ == '__main__' : 
    with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):    
        app.run(debug=False, use_debugger = False, use_reloader = False, port = 8081, host = '0.0.0.0')
