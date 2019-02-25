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
    try:
        # on connect - remove old auth file if exists
        if os.path.exists(os.path.join(Dirs()['LOG'], 'icloud_authentication')):
            os.remove(os.path.join(Dirs()['LOG'], 'icloud_authentication'))
            m.logger.info('old auth file removed')
    except:
        pass
    api = PyiCloudService(email,password)
    return api

def FilterDict(the_dict, keys):
    return {k: str(v) for k, v in the_dict.items() if k in keys}

def iCloudCal(api,date):
    events = api.calendar.events(date, date + datetime.timedelta(days = 1))
    attribs = ['localStartDate', 'localEndDate', 'duration', 'alarms'] #changed to local > otherwise UTC for recurret events - wrong
    parsed_events = {}
    for e in events:
        if e['title'] not in parsed_events.keys(): parsed_events[e['title']] = {}
        for a in attribs: parsed_events[e['title']][a] = e[a]
    m.logger.debug('EVENTS FOR DEBUG' + str(events)) #!!!: for testing > preserve all
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
def request_2FA(api):
    "returns device OR false if cant sent code"
    if api.requires_2fa:
   #     import click
        m.logger.info ("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            m.logger.info ("  %s: %s" % (i, device.get('deviceName', "SMS to %s" % device.get('phoneNumber'))))

        # device = 0# click.prompt('Which device would you like to use?', default=0)
        if devices is None:
            m.logger.error('None devices'); return False
        if len(devices) == 0:
            m.logger.error('Len(devices) == 0'); return False

        device = devices[0]
        if not api.send_verification_code(device):
            m.logger.error ("Failed to send verification code")
            return False
        else:
            m.logger.info('verification code sent')
            Speak('verification code sent')
        return device
    else:
        m.logger.info('api.requires_2fa is {} ? authentication not required?'.format(str(api.requires_2fa)))
        return True

#%% authentication manual > for pa_service
def re_authenticate(api): # api must already exists
    """request re-authentication
    # 1. stop attempts
    # 2. speak (with interval)
    # 3. check file with auth code in LOG (created by gunicorn's method)
    # 4. delete file and proceed
    """
    Speak('icloud requires authentication')
    device = request_2FA(api)
    if device == False: # code not sent
        Speak('error sending authentication code request')
        return False
    elif device == True:
        Speak('Authentication is not required')
        return True
    time.sleep(10)

    # checking every 3 sec / speaking every 3 min
    while not os.path.exists(os.path.join(Dirs()['LOG'], 'icloud_authentication')):
        Speak('waiting for icloud code')
        for check in range(0, 3*60):
            if os.path.exists(os.path.join(Dirs()['LOG'], 'icloud_authentication')):
                break
            time.sleep(3)

    code = open(os.path.join(Dirs()['LOG'], 'icloud_authentication'),'r').read()[:6] # removeing /n
    os.remove(os.path.join(Dirs()['LOG'], 'icloud_authentication'))

    m.logger.info('authentication recieved. code {}'.format(code))
    Speak('authentication code recieved')

    if not api.validate_verification_code(device, code):
        m.logger.error('Failed to verify verification code')
        Speak('Failed to verify verification code')
        return False
    else:
        # passed
        m.logger.info('authentication (should be) passed')
        Speak('icloud authentication complete')
        return True


if __name__ == '__main__':
    logger = LOGGER('icloud')
    if len(sys.argv) > 1:
        if '2fa' in sys.argv or '2FA' in sys.argv or '-2fa' in sys.argv or '-2FA' in sys.argv:
            logger.info ('requesting authentication')
            api = iCloudConnect()
            if re_authenticate(api):
                logger.info ('authentication complete'); Speak('authentication complete')
            else:
                logger.fatal('authentication failed'); Speak('authentication failed')
