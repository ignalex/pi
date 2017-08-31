# -*- coding: utf-8 -*-
"""
server listenning to GIT hook command to pull the master
Created on Wed Aug 30 08:35:00 2017
@author: ignalex
"""
#TODO: secure / payload 
#DONE: speak on update 
#DONE: email feedback > after secured config     
#TODO: restart particular apps 
#TODO: speak commit message
#TODO: secure path 

from __future__ import print_function
from flask import Flask, request
from common import LOGGER, Dirs, CONFIGURATION#, MainException
from send_email import sendMail
from speak_over_ssh import Speak
import pickle, os, datetime
from subprocess import Popen, PIPE
import daemon, socket

logger = LOGGER('git_hook')
p = CONFIGURATION()

app = Flask(__name__)

@app.route("/git_pull", methods=['POST'])
def git_pull():
    global logger, p
    j = request.json # payload
    with open(os.path.join(Dirs()['LOG'],'git_payload_{}.pcl'.format(str(datetime.datetime.now()))), 'wb') as f: 
        pickle.dump(j, f)
    
    #checking payload 
    if j['head_commit']['committer']['email'] != p.GIT_CI.check_committer: 
        Speak('commit security check not passed')
        logger.error('commit security check not passed')
        return 'commit security check not passed'
    
    process = Popen('git pull'.split(' '), stdout=PIPE, stderr=PIPE, cwd=Dirs()['REPO'])
    reply  = ' : '.join([str(i) for i in process.communicate() ]) 
    logger.info(reply)
    if p.GIT_CI.report_pull_email == 'YES' or p.GIT_CI.report_pull_email == True: 
        logger.info(sendMail([p.email.address], [p.email.address, p.email.login, p.email.password], 'CI - git pull from ' + socket.gethostname(), reply ,[]))
    if p.GIT_CI.report_speak == 'YES' or p.GIT_CI.report_speak == True: 
        Speak('git pull with the message {} done on the machine {}'.format(', '.join([i['message'] for i in j['commits']]), socket.gethostname()))
    return reply 

if __name__ == '__main__' : 
    with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):    
        app.run(debug=False, use_debugger = False, use_reloader = False, port = 8081, host = '0.0.0.0')
