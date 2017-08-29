# -*- coding: utf-8 -*-
"""
server listenning to GIT hook command to pull the master

Created on Wed Aug 30 08:35:00 2017
@author: ignalex
"""
from __future__ import print_function
from flask import Flask
from common import LOGGER # Dirs, CONFIGURATION, MainException,
from subprocess import Popen, PIPE
import daemon


logger = LOGGER('git_hook')
app = Flask(__name__)

@app.route("/test")
def test():
    global logger 
    logger.info('test')
    return 'test'
    
@app.route("/git_pull", methods=['POST'])
def git_pull():
    global logger 
    process = Popen('git pull'.split(' '), stdout=PIPE, stderr=PIPE, cwd=r'/home/pi/git/pi/')
    stdout, stderr = process.communicate() 
    reply  = str(stdout) + ' : ' + str(stderr)
    logger.info(reply)
    return reply 
    
    return 'git pull'

if __name__ == '__main__' : 
    with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):    
        app.run(debug=False, use_debugger = False, use_reloader = False, port = 8081, host = '0.0.0.0')
