# -*- coding: utf-8 -*-
"""watering module / updated
* to be run under sudo """

import sys 
from modules.relay import cascade 
from modules.speak_over_ssh import Speak
from modules.weather import WEATHER
from modules.common import LOGGER, CONFIGURATION

def extra_for_weather(threshhold=20, extra=2, was_raining=5): 
    w = WEATHER(False)
    w.ToInt()

    if w.WasRaining(was_raining): 
        Speak('it was raining for '+ str(w.rain) + ' mm yesterday. I will not water the plants' )
        logger.info('it was raining for '+ str(w.rain) + ' mm yesterday. I will not water the plants')
        sys.exit()
    
    result = [(w.temp_today - threshhold) * extra if (w.temp_today - threshhold) > 0 else 0][0] 
    Speak('temperature forecasted ' + str(w.temp_today) + ' degrees. adding ' + str(result) + ' seconds for watering')       
    logger.info('temperature forecasted ' + str(w.temp_today) + ' degrees. adding ' + str(result) + ' seconds for watering')
    return result 
  
   
def water(params):     
    "main triggering"
    for n, config in params.items():         
        cascade([config['relay'],config['motor']], 1, config['time'] )


#%%
if __name__ == '__main__': 
    logger = LOGGER('watering','INFO', True)
    p = CONFIGURATION()
    
    extra_time = extra_for_weather(p.water.extra_threshold, p.water.extra,p.was_raining)
#    params = {1 : {'relay': 2, 'motor' : 1, 'time' : 20  + extra_time}, 
#              2 : {'relay': 3, 'motor' : 1, 'time' : 30  + extra_time}} 

    params = {1 : {'relay': p.pins.water1, 'motor' : p.pins.motor, 'time' : p.water.time1  + extra_time}, 
              2 : {'relay': p.pins.water2, 'motor' : p.pins.motor, 'time' : p.water.time2  + extra_time}} 
    water(params)