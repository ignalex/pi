# -*- coding: utf-8 -*-
"""
Created on Mon Aug 04 17:12:41 2014

@author: aignatov
"""
from pyicloud import PyiCloudService
import datetime
from modules.common import CONFIGURATION
import __main__ as m

p = CONFIGURATION()

def iCloudConnect(email=p.iCloud.email, password=p.iCloud.password):
    #m.logger.info('c1 ,')
    api = PyiCloudService(email,password)
    #m.logger.info('c2 ,')
    return api

def FilterDict(the_dict, keys):
    return {k: str(v) for k, v in the_dict.items() if k in keys}

def iCloudCal(api,date):
    events = api.calendar.events(date, date + datetime.timedelta(days = 1))
    attribs = ['startDate', 'endDate', 'duration', 'alarms']
    parsed_events = {}
    for e in events:
        if e['title'] not in parsed_events.keys(): parsed_events[e['title']] = {}
        for a in attribs: parsed_events[e['title']][a] = e[a]
    return parsed_events

def iCloudLocation(api):
    keys = ['longitude', 'latitude','horizontalAccuracy', 'timeStamp']
    loc = FilterDict(api.iphone.location(), keys)
    loc['timeStamp'] = datetime.datetime.fromtimestamp(float(loc['timeStamp'])/1000)
    loc['timeAquired'] = datetime.datetime.now()
    return loc

def InstantLocation(api):
    loc = iCloudLocation(api)
    return (loc['longitude'], loc['latitude'])

def AllEvents():
    'returns the string of all todays events'
    ev = iCloudCal(iCloudConnect(), datetime.datetime.today())
    m.logger.debug('read from iCloud > \n' + str(ev))
    return ', '.join([(k + ' at ' + ' '.join([str(i) if i != 0 else '' for i in v['startDate'][4:6]])) for (k,v) in ev.items() if v['startDate'][3] == datetime.date.today().day])