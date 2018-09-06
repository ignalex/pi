# -*- coding: utf-8 -*-
"""
WEATHER module
- scans feeds from BOM
- scans temperature sensor from GPIO

returned results shape:

humidity 44.0
pressure 1020.4
rain 0.0
temp_in 21.5
temp_out 17.3
temp_today 18.0
wind 17.0
wind_gust 22.0

have to provide the link to BOM > for Sydney / Kurraba Point :
http://rss.weatherzone.com.au/?u=12994-1285&lt=aploc&lc=624&obs=1&fc=1&warn=1


Created on Tue Jan 27 10:58:24 2015

@author: aignatov
"""
from __future__ import print_function

try:
    import urllib2 #TODO: replace for PY3 compatibility
except:
    pass
import os, datetime, sys
sys.path.append('/home/pi/git/pi') # for running from command line.
from modules.common import Dirs, CONFIGURATION
p = CONFIGURATION()


if os.name == 'posix':
    try:
        from temperature import Temp
    except:
        pass

class WEATHER(object):
    def __init__(self,TempIn = True, LightSensor=True):
        self.link = p.WEATHER_LINK
        self.Log = os.path.join(Dirs()['LOG'],'sensors.log')
        self.call = {'rain' : ["<b>Rain:</b> ","mm since"],
                     'temp_out' : ["<b>Temperature:</b> ","&#"],
                     'humidity' : ["<b>Relative humidity:</b> ","%<br"],
                     'pressure' : ["<b>Pressure:</b> "," hPa"],
                     'wind'     : ["<b>Wind:</b> "," km/h"," at "],
                     'wind_gust': ["gusting to "," km/h"],
                     'temp_today' : ['C - ','&#176;']}
        self.readings = {}
        try:
            self.html = urllib2.urlopen(self.link,timeout = 10).read()
            self.timeout = False
        except:
            self.timeout = True
            return

        for k,v in self.call.items(): self.Process(k,v)
        self.rain_at_all = [True if float(i) > 0 else False for i in [self.rain]][0]
        self.DateTime()
        if os.name == 'posix' and TempIn: self.TempIn()
        if LightSensor: self.LightSensor()
        self.Forecast()
    def Process(self,name,f):
        f1_pos = self.html.find(f[0])+len(f[0])
        f2_pos = self.html.find(f[1],f1_pos)
        found = self.html[f1_pos:f2_pos]
        if len(f) == 3:
            found = found.split(f[2])[-1]
        try:
            setattr(self,name,float(found))
        except:
            setattr(self,name,None)
    def Forecast(self):
        name,f =  'forecast', ['<img src="http://www.weatherzone.com.au/images/icons/fcast_30/','.gif']
        f1_pos = self.html.find(f[0])+len(f[0])
        f2_pos = self.html.find(f[1],f1_pos)
        found = self.html[f1_pos:f2_pos]
        if len(f) == 3:
            found = found.split(f[2])[-1]
        setattr(self,name,found.replace('_',' '))

    def TempIn(self):
        self.temp_in = Temp()
        self.call['temp_in'] = ["",""]

    def LightSensor(self):
        self.light = light_sensor()
        self.call['light'] = ["",""]
                
    def DateTime(self):
        f = ["<pubDate>"," +"]
        f1_pos = self.html.find(f[0])+len(f[0])+5
        f2_pos = self.html.find(f[1],f1_pos)
        self.now = datetime.datetime.strptime(self.html[f1_pos:f2_pos],'%d %b %Y %H:%M:%S')
    def ToInt(self):
        for r in self.call.keys():
            if getattr(self,r) is not None:
                setattr(self,r,int(getattr(self,r)))
    def Report(self, LOG = True):
        for r in sorted(self.call.keys()):
            print (r, getattr(self,r))
            self.readings[r] = getattr(self,r)
            if LOG:
                print (str(self.now)[:-3] + '\t' +r + '\t' + str(getattr(self,r)), file= open(self.Log, 'a'))

    def WasRaining(self,mm=3):
        if self.rain >= mm:
            return True
        else:
            return False

def light_sensor(link='http://192.168.1.175/sensor'): 
    try: 
        html = urllib2.urlopen(link,timeout = 3).read()
        f1_pos = html.find('<body>\n')+15
        f2_pos = html.find('\n',f1_pos)
        light = html[f1_pos : f2_pos]
        return light
    except: 
        return None
    

def to_db(w):
    print ('adding to db')
    from modules.postgres import PANDAS2POSTGRES
    import pandas as pd
    try:
        con = PANDAS2POSTGRES(p.hornet_pi_db.__dict__)
        con.write(pd.DataFrame.from_dict(w, orient='index').T, 'weather')
        return True
    except Exception as e:
        print (str(e))

if __name__ == '__main__':
    args = sys.argv[1:]
    w = WEATHER()
    if not w.timeout: w.Report()
    
    if '-DB' in args:
        w.readings['datetime'] = datetime.datetime.now()
        status = to_db(w.readings)
        print('to DB ' + str(status))

