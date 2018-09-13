# -*- coding: utf-8 -*-
"""
Created on Mon Aug 04 17:12:41 2014

@author: aignatov
"""
from __future__ import print_function

from pyicloud import PyiCloudService
import datetime, sys, os, time
sys.path.append('/home/pi/git/pi')
from modules.common import CONFIGURATION, Dirs, LOGGER
from modules.talk import Speak
import __main__ as m

p = CONFIGURATION()

def iCloudConnect(email=p.iCloud.email, password=p.iCloud.password):
    api = PyiCloudService(email,password)
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

#%% 2FA
def get2FA(api):
    if api.requires_2fa:
        import click
        print ("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print ("  %s: %s" % (i, device.get('deviceName',
                "SMS to %s" % device.get('phoneNumber'))))

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print ("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print ("Failed to verify verification code")
            sys.exit(1)
        # adding mark (file) that authentication passed
        print ('authenticated', file=open(os.path.join(Dirs()['LOG'], 'icloud_authentication'), 'w'))

#%% authentication manual > for pa_service
def re_authenticate():
    """request re-authentication
    # 1. stop attempts
    # 2. speak (with interval)
    # 3. check externally if manual update done
    # 4. proceed
    """
    while not os.path.exists(os.path.join(Dirs()['LOG'], 'icloud_authentication')):
        Speak('icloud requires authentication')
        time.sleep(5 * 60)
    os.remove(os.path.join(Dirs()['LOG'], 'icloud_authentication'))
    m.logger('authentication (should be) passed')
    Speak('icloud authentication complete')


if __name__ == '__main__':
    logger = LOGGER('icloud')
    if len(sys.argv) > 1:
        if '2fa' in sys.argv:
            logger.info ('requesting authentication')
            api = iCloudConnect()
            get2FA(api)