# -*- coding: utf-8 -*-
"""
locking for the time when communication to adruino is in place
** needed to syncronise coms to arduino from concurrent threads 

Created on Fri Jul 25 09:36:29 2014
@author: aignatov
"""
from __future__ import print_function

import datetime, os 
from time import sleep 
#TODO: LOG autocreate (Shell)

class LockArd(object):
    def __init__(self, ID = 'py'):
        self.locking_file = os.path.join([i for i in ['/home/pi/LOG/','/home/pi/PYTHON/GPIO/LOG/','/storage/PYTHON/GPIO/LOG/',os.getcwd()] if os.path.exists(i)][0], ID +'.lck')
        self.force_sec = 15
        self.ID = ID
        self.locked_by = ''
    def __enter__(self): 
        self.Lock()
    def __exit__(self, type, value, traceback):
        sleep(0.1)
        self.Unlock()
    def Lock(self): 
        while True: 
            try: 
                self.status = open(self.locking_file,'r').read() 
                self.secs = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(self.locking_file))).seconds
            except: 
                self.status = ''            
            if self.status in ['\n', '', '\r\n'] or self.secs > self.force_sec: # after N sec forcly take the control 
                 print (self.ID , file =  open(self.locking_file, 'w'))
                 return True 
            else: 
                #print 'locked by ' + self.status
                pass 
            sleep(0.5)
    def Unlock(self): 
        print ('', file = open(self.locking_file, 'w'))
        
        
if __name__ == '__main__': 
    import sys 
    ID, delay = sys.argv[1], int(sys.argv[2])
    lock = LockArd(ID)
    
    for a in range(1,10): 
        lock.Lock()
        print ('doing something' )
        sleep(delay)
        lock.UnLock()
        sleep(1)