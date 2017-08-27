# -*- coding: utf-8 -*-
"""
lamp module 
* to be run from under MS 

Created on Fri Apr 25 13:12:30 2014
@author: ignalex

"""
import datetime 
import __main__ as m 

#TODO: move into MS, as it can't be used by itself 

def lamp(TASK): 
    "to be used only from inside MS"
    "dependencies: esp, log, sunrise"
    if TASK == []: 
        m.log('Lamp module: Not enough argument')

    twilight = m.Sun(datetime.date.today())
    now = datetime.datetime.now()    

    if TASK == ['ON'] and (now <= twilight[0] or now >= twilight[1]): # turm ON only if dark  
        # lamp ON 
        m.items.lamp.status = True
        m.log( 'lamp ON')
        try: 
            m.ESP(['6','rf433','light','on'])
            m.log('lamps are ON')
        except: 
            pass 
    elif TASK == ['ON'] and (now > twilight[0] and now < twilight[1]):
        m.log('day time. Lamp is not turned ON') 
    elif TASK == ['OFF']: # turn OFF at any time 
        # lamp off 
        m.items.lamp.status = False
        m.log( 'lamp OFF') 
        try: 
            m.ESP(['6','rf433','light','off'])
            m.log('lamps are OFF')
        except: 
            pass     