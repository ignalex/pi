# -*- coding: utf-8 -*-
"""watering module / updated
* to be run under sudo """

import sys 
from modules.relay import cascade 
from modules.speak_over_ssh import Speak
from modules.weather import WEATHER
from modules.common import LOGGER, CONFIGURATION

def extra_for_weather(threshhold=20, extra=2, was_raining=5,min_temp=0): 
    w = WEATHER(False)
    w.ToInt()

    # if min_temp > 0 - checking if actual temp > min_temp and watering only if yes
    if min_temp > 0 and w.temp_today <= min_temp: 
        Speak('it is too cold for extra watering' )
        logger.info('temperature forecasted ' + str(w.temp_today) + ' less than ' + str(min_temp))
        sys.exit()

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
    water_set = getattr(p,[sys.argv[1] if len(sys.argv)>1 else 'water1'][0]) #choosing one referenced from cmd
    
    extra_time = extra_for_weather(water_set.extra_threshold, water_set.extra,water_set.was_raining, water_set.min_temp)

    params = {1 : {'relay': p.pins.water1, 'motor' : p.pins.motor, 'time' : water_set.time1  + extra_time}, 
              2 : {'relay': p.pins.water2, 'motor' : p.pins.motor, 'time' : water_set.time2  + extra_time}} 
    water(params)