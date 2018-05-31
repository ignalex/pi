# -*- coding: utf-8 -*-
"""
Created on Mon Dec 07 06:48:31 2015

@author: Alex
"""
from __future__ import print_function
import pandas as pd 
import requests, datetime, os, time , math 

# disabling warning message
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from common import  LOGGER, Dirs, CONFIGURATION, MainException
from postgres import PANDAS2POSTGRES

class GET_API(object): 
    """generic API call request class"""
    def __init__ (self,url = "", params = None, name = "",proxies = ""): 
        self.url, self.params = url, params
        self.proxies =  proxies 
        #self.auth =requests.auth.HTTPBasicAuth('login', 'pass') 
        self.response = requests.get(url = self.url, params = self.params, proxies = self.proxies, verify = False) #, auth = self.auth) 
        if self.response.status_code == 200: self.Parse(name)
    def Parse(self,name): 
        setattr(self,name,self.response.json()) 

class ISS(GET_API): 
    """ISS postition and people class v 2 - realtime """
    def __init__(self): 
        GET_API.__init__(self,url = "https://api.wheretheiss.at/v1/satellites/25544", params = None, name = 'iss',proxies = proxies)    
        self.keys = ['timestamp','latitude','longitude','velocity','altitude']
        for k in self.keys: setattr(self,k,self.iss[k])
        self.timestamp = datetime.datetime.fromtimestamp(self.timestamp)
        self.HowFar()
    def HowFar(self): 
        self.how_far = int(Distance(location,(( self.longitude,self.latitude)))/1000)
    def Log(self):       
        print ('\t'.join([str(getattr(self,i)) for i in self.keys + ['how_far']]) )
        #to DB 
        self.df = pd.DataFrame.from_dict({i : getattr(self,i) for i in self.keys + ['how_far']}, orient='index').T
        con.write(self.df, 'iss_position', if_exists='append')
        
        if alert: 
            Alert(self.how_far)

def Distance(origin, destination):
    lon1, lat1 = [float(i) for i in origin]
    lon2, lat2 = [float(i) for i in destination]
    radius = 6371000 # km

    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d

def Alert(distance): 
    global alert_time, iss 
    if distance <= alert_distance: 
        if (datetime.datetime.now() - alert_time).seconds > 5 * 60 : #and \
        #((datetime.datetime.now().hour > alert_time_window[0]) and (datetime.datetime.now().hour < alert_time_window[1])): 
            if alert_type == 'speak': 
                os.system('python /home/pi/git/pi/modules/talk.py "international space station approaching, distance is {0} kilometers"'.format(str(distance)))
            elif alert_type == 'print': 
                print ('international space station approaching, distance is {0}'.format(str(distance)))
            alert_time = datetime.datetime.now()
        print ('\t'.join([str(i) for i in [str(datetime.datetime.now()).split('.')[0], distance, iss.latitude, iss.longitude]]), open(os.path.join(Dirs()['LOG'], 'iss_alert'),'a'))

def Start(): 
    global iss, delay
    last_time_stamp = None
    while True: 
        iss = ISS()
        if iss.timestamp != last_time_stamp: iss.Log()
        last_time_stamp =  iss.timestamp    
        time.sleep(delay)
         
if __name__ == '__main__': 

    #DONE: logger + data > to DB 
    logger = LOGGER('iss', 'INFO')
    p = CONFIGURATION()
    con = PANDAS2POSTGRES(p.hornet_pi_db.__dict__)
    
    delay = 10 # secs 
    location = (151.2, -33.85)
    alert, alert_type, alert_distance, alert_time, alert_time_window = True, 'speak', 500, datetime.datetime.now() - datetime.timedelta(hours = 12), (6,21) # initital time > setting to yesterday 
    proxies = {}
    try: 
        logger.info('starting')
        Start()
    except: 
        MainException()
