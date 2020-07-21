# -*- coding: utf-8 -*-
"""
Created on Mon Dec 07 06:48:31 2015

@author: Alex

#DONE: logger + data > to DB
#MAYBE: distance calc from DB
#DONE: indexes to DB + geom + make table instead of pandas
#DONE: silence during night + when speaking > still scanning
#TODO: when approaching > reduce delay
#TODO: alert only once per approach > accumulate and send once
#DONE: class initiate only once
#TODO: simplify table structure > staging > geom
#TODO: ask where > answer continent / country
#TODO: projection for when passing

"""
from __future__ import print_function
import requests, datetime, os, time , math

# disabling warning message # somehow still goes on Pi
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from common import  LOGGER, Dirs, CONFIGURATION, MainException
from postgres import PG_Connect# PANDAS2POSTGRES
from send_email import sendMail
from talk import  Speak

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
        self.keys = ['timestamp','latitude','longitude','velocity','altitude']
    def Scan(self):
        GET_API.__init__(self,url = "https://api.wheretheiss.at/v1/satellites/25544", params = None, name = 'iss',proxies = proxies)
        for k in self.keys: setattr(self,k,self.iss[k])
        self.timestamp = datetime.datetime.fromtimestamp(self.timestamp)
        self.how_far = int(Distance(location,(( self.longitude,self.latitude)))/1000)
    def Log(self):
        print ('\t'.join([str(getattr(self,i)) for i in self.keys + ['how_far']]) )
        #to DB
        sql = "insert into iss_position (timestamp,latitude,longitude,velocity,altitude,how_far) values ('{}',{},{},{},{},{})".\
            format(self.timestamp, self.latitude, self.longitude, self.velocity, self.altitude, self.how_far)
        cur.execute(sql)
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
        if (datetime.datetime.now() - alert_time).seconds > 5 * 60 :
            alert_time = datetime.datetime.now()
            if alert_type == 'speak' and alert_time.hour > alert_time_window[0] and alert_time.hour < alert_time_window[1]:
                Speak("international space station approaching, distance is {0} kilometers".format(str(distance)))

        alert_message = '\t'.join([str(i) for i in [str(datetime.datetime.now()).split('.')[0], distance, iss.latitude, iss.longitude]])
        print (alert_message, file=open(os.path.join(Dirs()['LOG'], 'iss_alert'),'a'))
        logger.info(alert_message)
        logger.info('sending email ... ' + sendMail([p.email.address], [p.email.address, p.email.login, p.email.password], 'ISS approaching alert ', alert_message ,[]))

def Start():
    global iss, delay
    last_time_stamp = None
    iss = ISS()
    while True:
        iss.Scan()
        if iss.timestamp != last_time_stamp: iss.Log()
        last_time_stamp =  iss.timestamp
        time.sleep(delay)

if __name__ == '__main__':

    logger = LOGGER('iss', 'INFO')
    p = CONFIGURATION()

    con, cur = PG_Connect(getattr(p,p.ISS.db).__dict__)

    delay = int(p.ISS.delay) # secs
    location = (151.2, -33.85)
    alert, alert_type, alert_distance, alert_time, alert_time_window = True, 'speak', int(p.ISS.alert_distance), datetime.datetime.now() - datetime.timedelta(hours = 12), (6,21) # initital time > setting to yesterday
    proxies = {}
    time.sleep(delay) # to manage SSL entropy on reboot
    try:
        Speak('I monitor ISS position, will let you know if it is within {} km'.format(alert_distance))
        logger.info('starting')
        Start()
    except:
        MainException()
        Speak('ISS scanning stopped')

