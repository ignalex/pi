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

import bluetooth

try:
    from common import CONFIGURATION, Dirs, Platform
except:
    from .common import CONFIGURATION, Dirs, Platform

#TODO: config MAC to outside func
#TODO: esp signal on ON / OFF

def PingIPhoneOnce(source = 'BT', log = True):
    if source == 'BT':
        result =  PingBT()
    elif source == 'WF':
        result =  PingIP()
    elif source == 'Hornet':
        result =  PingHornet()
    return result

def PingIP(IP = '7'):
    "ping device via wifi by IP. not stable for dynamic IPs, but still usefull; doesnt work as Wifi on dev can sleep"
    IP = str(IP)
    if IP.isdecimal() : IP = "192.168.1."+IP # fof consistency
    cmd = ["ping","-c","1", "-W", "2", IP]
    if Platform()[0]: cmd = ['sudo'] + cmd # "sudo", - FOR RASPBIAN

    try:
        stdout, stderr = Popen(cmd, stdout=PIPE, stderr=PIPE).communicate(timeout=5)
    except:
        #  timeout
        return [False,None]

    REPLIES  = {b"0 packets received" : False,
                b"1 packets received"  : True,
                b"1 received" : True}
    print (str (cmd))
    print (str(stdout))
    try:
        return [[ v for k,v in REPLIES.items() if str(stdout).find(k) != -1][0],None]
    except:
        return [False,None]

def PingBT(MAC=CONFIGURATION().BT.MAC, BT_METHOD=CONFIGURATION().BT.METHOD):
    "BT_METHOD : self, ssh_shrimp [alike], bluetooth"
    # pairing https://www.cnet.com/how-to/how-to-setup-bluetooth-on-a-raspberry-pi-3/

    com = "sudo l2ping -s 1 -c 1 -t 4 "+MAC
    #if socket.gethostname() != 'RaspPI': com.insert(0,'sudo')
    if BT_METHOD.lower() == 'self':
        com = com.split(' ')
        return RunCMD_BT(com)
    elif BT_METHOD.lower().startswith('ssh'):
        bt=BT_METHOD.lower().replace('ssh_','')
        com = ('ssh -i /home/pi/.ssh/{} pi@{}.local '.format(bt,bt) + com).split(' ')
        return RunCMD_BT(com)
    elif BT_METHOD.lower() == 'bluetooth':
        start = datetime.now()
        result = bluetooth.lookup_name(MAC) is not None
        return [result, (datetime.now() - start).microseconds/10 ] #  status, milliseconds
    else:
        print('BT_METHOD not recognized')
        return [None,None]


def RunCMD_BT(com):
    try:
        stdout, stderr = Popen(com, stdout=PIPE, stderr=PIPE).communicate(timeout=10)
    except Exception as e:
        print(str(e))
        return [False,None]

    ERRORS  = {"Can't connect: Connection refused\n" : True,
               "Can't connect: Host is down\n" : False,
               "Can't connect: Permission denied\n" : True}
               #"1 received" : True }

    REPLIES = [b'bytes from', b'recieved']

    if stderr in ERRORS.keys():
        return [ERRORS[stderr],None]
    elif True in [False if j == -1 else True for j in [stdout.find(i) for i in REPLIES]]:
        ms = stdout[stdout.find(b'time ') + 5: stdout.find(b'ms')+2]
        return [True, ms]
    else:
        return [False,None]

#TODO: get log filder func into shell
def Log(result):
    log = os.path.join(Dirs()['LOG'],'log_ping_iPhone.txt')
    print (str(datetime.now()).split('.')[0] + '\t' + str(result), file = open(log,'a'))

def PingIPhone(N=4,S=5): # was 1, 0
    " N times to ping, S - sleep"
    response, log = [], []
    for n in range(0,N):
        #print 'pinging ', n
        response.append(PingIPhoneOnce())
        # Log('\t'.join([str(i) for i in [n,N,S,response[-1][0]]])) #!!!: False to LOG > issue with AcquireResult - false from 1st attempt
        log.append('\t'.join([str(i) for i in [n,N,S,response[-1][0] ]]))
        if response[-1][0] == True:
            for f in log: Log(f)
            return True
        sleep(S)

    # status to file
    for f in log: Log(f) #finally log
    return True in [i[0] for i in response]

class PING(object):
    def __init__(self,N=4,S=5):
        self.status = True # presume I am around at the start moment
        self.current = True
        self.True_history = []
        self.previous_status = None
        self.changed = None
        self.N = N
        self.S = S
        #self.Ping()
        #self.Status()
    def Ping(self):  # immidiate result + checking
        self.current = PingIPhone(self.N, self.S)
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

    com =  "tail -1 " + os.path.join(Dirs()['LOG'],'log_ping_iPhone.txt')
    stdout, stderr = Popen(com.split(' '), stdout=PIPE, stderr=PIPE).communicate()

    if type(stdout) != str : stdout = stdout.decode("utf-8") #for python3 > return is Byte like object

    #return LAST False / True
    return stdout.replace('\n','').split('\t')[-1] != 'False'

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

