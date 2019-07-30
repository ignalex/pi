# -*- coding: utf-8 -*-
"""
WEATHER module
- scans feeds from BOM
- scans temperature sensor from GPIO

returned results shape:

humidity 55.0
light_1 1001
light_2 1038
pressure 1025.7
rain 0.0
temp_in 23.56
temp_out 19.6
temp_today 20.0
wind 26.0
wind_gust 35.0

have to provide the link to BOM > for Sydney / Kurraba Point :
http://rss.weatherzone.com.au/?u=12994-1285&lt=aploc&lc=624&obs=1&fc=1&warn=1

#DONE: solar envoy scan
#DONE: internal temp / humidity scan

Created on Tue Jan 27 10:58:24 2015
@author: aignatov
"""
from __future__ import print_function
import __main__ as m
import requests
from random import random
from statistics import mean

import os, datetime, sys
sys.path.append('/home/pi/git/pi') # for running from command line.
sys.path.append('/home/pi/git/pi/modules') # for compat
from modules.common import Dirs, CONFIGURATION, LOGGER
p = CONFIGURATION()


if os.name == 'posix':
    try:
        if  hasattr(p,'temperature'):
            if p.temperature.source == '1wire':
                from temperature import Temp
            elif p.temperature.source == 'dht11':
                from dht11 import Temp
        else:
            from temperature import Temp
    except:
        try:
            from dht11 import Temp
            print('Temp from dht11')
        except:
            pass #print ('no temperature imported')
    try:
        from dht11 import dht11
    except:
        pass #print ('no dht11 imported')

#DONE: separeate creating and reading
class WEATHER(object):
    def __init__(self,TempIn = True, LightSensor=True,  dht=False, solar=False):
        """if p.weather.{element} exists, it will overwrite DEFAULT (p configuration for host)
        """
        self.link = p.WEATHER_LINK
        self.Log = os.path.join(Dirs()['LOG'],'sensors.log')
        self.config = {}
        #logic : if no P elements, use the defaults
        for name, default in {'TempIn' : TempIn,
                              'LightSensor' : LightSensor,
                              'dht' : dht,
                              'solar': solar}.items():
            self.config[name] = (getattr(p.weather,name) if hasattr(p.weather, name) else default) \
                                if hasattr(p,'weather') else default
        self.Update()

    def Update(self):
        self.call = {'rain' : ["<b>Rain:</b> ","mm since"],
                     'temp_out' : ["<b>Temperature:</b> ","&#"],
                     'humidity' : ["<b>Relative humidity:</b> ","%<br"],
                     'pressure' : ["<b>Pressure:</b> "," hPa"],
                     'wind'     : ["<b>Wind:</b> "," km/h"," at "],
                     'wind_gust': ["gusting to "," km/h"],
                     'temp_today' : ['C - ','&#176;']}

        self.readings = {}
        try:
            self.html = requests.request('GET',self.link,timeout = 10).text
            self.timeout = False
        except:
            self.timeout = True
            return
        if self.html == '': # error on remote side
            self.rain_at_all = False
            self.rain = 0
            self.temp_out = 20
            self.temp_today = 20
            return
        for k,v in self.call.items(): self.Process(k,v, self.html) # weather html

        self.rain_at_all = [True if float(i) > 0 else False for i in [self.rain]][0]
        self.DateTime()
        if self.config['TempIn']:       self.TempIn()
        if self.config['LightSensor']:  self.LightSensor()
        if self.config['dht']:          self.DHT11()
        if self.config['solar']:        self.Solar()
        self.Forecast()
        self.Report(False, False)

    def Process(self, name, f, html):
        f1_pos = html.find(f[0])+len(f[0])
        f2_pos = html.find(f[1],f1_pos)
        found = html[f1_pos:f2_pos]
        if len(f) == 3:
            found = found.split(f[2])[-1]
        try:
            setattr(self,name,float(found))
        except:
            try:
                setattr(self,name,float(found.replace(' ','')))  # removing spaces.
            except:
                setattr(self,name,None)
    def Forecast(self): #TODO: logic same > integrate better
        name,f =  'forecast', ['<img src="http://www.weatherzone.com.au/images/icons/fcast_30/','.gif']
        f1_pos = self.html.find(f[0])+len(f[0])
        f2_pos = self.html.find(f[1],f1_pos)
        found = self.html[f1_pos:f2_pos]
        if len(f) == 3:
            found = found.split(f[2])[-1]
        setattr(self,name,found.replace('_',' '))

    def TempIn(self, N=5):
        "average over N readings"
        temp_in = Temp()
        self.temp_in_hist = ((self.temp_in_hist if hasattr(self,'temp_in_hist') else []) + \
                             [float(temp_in)])[-N:]
        self.temp_in = round(mean(self.temp_in_hist),1)
        self.call['temp_in'] = ["",""]


    def LightSensor(self, sensors = {'light_1' : {'link': 'http://192.168.1.175/control/sensor', 'calibr' : 1},
                                     'light_2' : {'link': 'http://192.168.1.176/control/sensor/sound', 'calibr' : 1.2}}):
        for light, params in sensors.items():
            try:
                if datetime.datetime.now().hour < 5 or datetime.datetime.now().hour > 20:
                       params['link'] = params['link'].replace('/sound','')
                setattr(self, light, int(light_sensor(params['link']) * params['calibr']))
            except:
                setattr(self, light, None)
            self.call[light] = ["",""]
    def DHT11(self):
        "scan DHT11 sensor"
        temp_in, humid_in = dht11()

        setattr(self,'temp_in',float(temp_in))
        setattr(self,'humid_in',float(humid_in))
        self.call['temp_in'] = ["",""]
        self.call['humid_in'] = ["",""]

    def Solar(self):
        "scan solar html for current production"
        m.logger.debug('scanning solar')
#        self.solar = p.solar # config params
        try:
            self.link_solar = p.SOLAR_LINK
            self.html_solar = requests.request('GET',self.link_solar,timeout = 5).text
            for k,v in {'solar' : ["<td>Currently</td>    <td>","W</td></tr>"]}.items(): #!!!: here could be extra spaces
                self.Process(k,v, self.html_solar) # solar html
            self.call['solar'] = ["",""] #compatibility
            m.logger.debug('solar scanned : {} kW'.format(str(self.solar)))
        except Exception as e:
            m.logger.debug('cant scan solar URL\n' + str(e))
            #test
            self.call['solar'] = ["",""]
            self.solar = 500 + int(random() * 500) #!!!: turn off later
            return

    def DateTime(self):
        f = ["<pubDate>"," +"]
        f1_pos = self.html.find(f[0])+len(f[0])+5
        f2_pos = self.html.find(f[1],f1_pos)
        self.now = datetime.datetime.strptime(self.html[f1_pos:f2_pos],'%d %b %Y %H:%M:%S')

    def ToInt(self):
        for r in self.call.keys():
            if getattr(self,r) is not None:
                setattr(self,r,int(getattr(self,r)))

    def Report(self, LOG = True, PRINT = True):
        for r in sorted(self.call.keys()):
            if PRINT: print (r, getattr(self,r))
            self.readings[r] = getattr(self,r)
            if LOG:
                print (str(self.now)[:-3] + '\t' +r + '\t' + str(getattr(self,r)), file= open(self.Log, 'a'))
        self.readings['datetime'] = datetime.datetime.now()

    def WasRaining(self,mm=3):
        if self.rain >= mm:
            return True
        else:
            return False

def light_sensor(link='http://192.168.1.175/control/sensor'):
    try:
        light = int(requests.request('GET', link, timeout = 5).json()['data']['sensor'])
        return light
    except:
        return None

def to_db(w, con = 'local_pi_db'):
    "con to be set in one of the INI files, default to localhost"
    #TODO: into class > to be able to write from inside
    print ('adding to db')
    from modules.postgres import PANDAS2POSTGRES
    import pandas as pd
    try:
        con = PANDAS2POSTGRES(getattr(p,con).__dict__)
        con.write(pd.DataFrame.from_dict(w, orient='index').T, 'weather')
        return True
    except Exception as e:
        print (str(e))

if __name__ == '__main__':
    args = sys.argv[1:]
    logger = LOGGER('weather')
    w = WEATHER()
    if not w.timeout: w.Report()

    if '-DB' in args:
        logger.info(str(w.readings))
#        w.readings['datetime'] = datetime.datetime.now()
        status = to_db(w.readings)
        print('to DB ' + str(status))

