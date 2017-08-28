# -*- coding: utf-8 -*-
"""
after pairing PI with phone's BT, PI will ping it every ... for getting answer 'am I home?' used to turn on / off things
* pinging logic: several cycles allowed with False before return False (lost connection for short time etc.)


**theoretically for pinging bluetooth and wifi devices, but wifi not stable

"""
from __future__ import print_function
import sys, os, socket
from time import sleep 
from datetime import datetime, timedelta
from subprocess import Popen, PIPE

from common import CONFIGURATION, Dirs
#TODO: config MAC to outside func

def PingIPhoneOnce(source = 'BT', log = True): 
    if source == 'BT': 
        result =  PingBT()
    elif source == 'WF': 
        result =  PingWF()
    elif source == 'Hornet': 
        result =  PingHornet()
    return result 
    
def PingWF(IP = '155'): 
    "ping device via wifi by IP. not stable for dynamic IPs, but still usefull"
    # optionally : "sudo bluez-simple-agent hci0 E4:25:E7:E4:E6:E5" 
    # "sudo", - FOR RASPBIAN 
    
    process = Popen(["ping","-c","1","192.168.1."+IP], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    REPLIES  = {"0 packets received" : False, 
                "1 packets received"  : True}
    try:     
        return [[ v for k,v in REPLIES.items() if stdout.find(k) != -1][0],None]
    except: 
        return [False,None]

def PingBT(MAC=CONFIGURATION().BT): 
    # optionally : "sudo bluez-simple-agent hci0 E4:25:E7:E4:E6:E5" # CC:29:F5:93:7F:8D - new iPhone 6
    # 70:F0:87:D0:D7:73       SOMEONE’s iPhone 7 
    # "sudo", - FOR RASPBIAN 
    
#    sudo = ['' if i == 'RaspPI' else 'sudo' for i in [socket.gethostname()]][0]
    com = ["l2ping","-s","1","-c","1",MAC]
    if socket.gethostname() != 'RaspPI': com.insert(0,'sudo')
    process = Popen(com, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    ERRORS  = {"Can't connect: Connection refused\n" : True, 
               "Can't connect: Host is down\n" : False,
               "Can't connect: Permission denied\n" : True} 
               #"1 received" : True }
    
    REPLIES = ['bytes from', 'recieved']    
    
    if stderr in ERRORS.keys(): 
        return [ERRORS[stderr],None]
    elif True in [False if j == -1 else True for j in [stdout.find(i) for i in REPLIES]]: 
        ms = stdout[stdout.find('time ') + 5: stdout.find('ms')+2]
        return [True, ms]
    else: 
        return [False,None]

#TODO: get log filder func into shell 
def Log(result): 
    log = os.path.join(Dirs()['LOG'],'log_ping_iPhone.txt')
    print (str(datetime.now()).split('.')[0] + '\t' + str(result), file = open(log,'a'))  

def PingIPhone(N=4,S=5): # was 1, 0 
    " N times to ping, S - sleep" 
    response = []
    for n in range(0,N): 
        #print 'pinging ', n
        response.append(PingIPhoneOnce())
        Log('\t'.join([str(i) for i in [n,N,S,response[-1][0]]]))
        #print response[-1]
        if response[-1][0] == True: 
            return True 
        sleep(S)
    # status to file 
    
    if True in [i[0] for i in response]: 
        return True
    else: 
        return False

class PING(object): 
    def __init__(self): 
        self.status = True # presume I am around at the start moment 
        self.current = True 
        self.True_history = []
        self.previous_status = None
        self.changed = None
        #self.Ping()
        #self.Status()
    def Ping(self):  # immidiate result + checking 
        self.current = PingIPhone()
        if self.current: 
            self.True_history.append(datetime.now())
        if self.current != self.previous_status: # changed 
            self.changed = self.current
            self.previous_status = self.current
        else: 
            self.changed = None 
        return self.current # immidiate 
    def Status(self,delay=1): # delayed result
        if self.current == True: 
            self.status = True 
            return True
        else: 
            try: # if no history 
                if self.True_history[-1] + timedelta(minutes = delay) >  datetime.now(): 
                    self.status = True 
                    return True 
                else: 
                    self.status = False
                    return False
            except: 
                return False 
    def Pause(self,timings=[5,45]): # searching (False) + standby (True)
        return timings[int(self.status)]
#%%
#TODO: rename, remove hardcoding addresses
def PingHornet(): 
    """
    iPhone NEED TO BE PAIRED 
    doesn't work >>> http://www.correlatedcontent.com/blog/bluetooth-keyboard-on-the-raspberry-pi/
    https://kofler.info/bluetooth-konfiguration-im-terminal-mit-bluetoothctl/
    """
    process = Popen(["ssh","-p","2226","-i","/storage/.ssh/hornet","pi@192.168.1.153","nohup","sudo","python","/home/pi/PYTHON/GPIO/modules/PingIPhone.py"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stdout.startswith('True'): 
        return [True,None]
    else: 
        return [False,None]


def AcquireResult(allowed_delay_min = 5): 
    """using SSH, returns 1 / 0 / None if iphone is around (not directly pinging > only reading last logs) 
    if more time passed than allowed_delay_min since last ping > returns None *too old log
    ** to be run from another device with SSH / RSA keys on it"""

    path_to_log = '/home/pi/LOG/log_ping_iPhone.txt'
    com =  "tail -1 " + path_to_log

    process = Popen(com.split(' '), stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()    

    if ((datetime.now() + timedelta(seconds = 120)) - datetime.strptime(stdout.split('\t')[0],'%Y-%m-%d %H:%M:%S')).seconds < allowed_delay_min * 60 + 120 : 
        return stdout.replace('\n','').split('\t')[-1] == 'True'
    else: 
        print ((datetime.now() - datetime.strptime(stdout.split('\t')[0],'%Y-%m-%d %H:%M:%S')).seconds)
        return None
#%%
def MonitorForNMin(minutes): 
    "log result for N minutes (for heater integration)"
    start = datetime.now()
    iPhone = PING()
    print ('monitoring iPhone for {} minutes'.format(minutes))
    while datetime.now() < start + timedelta(minutes = minutes): 
        iPhone.Ping()
        print (str(datetime.now()).split('.')[0]  + ' ' + str(iPhone.status))
        sleep(iPhone.Pause())
    print ('stopping monitoring')
            
if __name__ == '__main__': 
    if len(sys.argv) >1: 
        MonitorForNMin(int(sys.argv[1]))
    else: 
        print (PingIPhone())
    
    