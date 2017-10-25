# -*- coding: utf-8 -*-
"""watering module / updated
* to be run under sudo """

import sys 
from modules.relay import cascade 
from modules.speak_over_ssh import Speak
from modules.weather import WEATHER
from modules.common import LOGGER, CONFIGURATION

def extra_for_weather(threshhold=20, extra=2, was_raining=5,min_temp_set=0): 
    w = WEATHER(False)
    w.ToInt()

    # if min_temp_set > 0 - checking if actual temp > min_temp_set and watering only if yes
    if min_temp_set > 0 and w.temp_today <= min_temp_set: 
        Speak('it is too cold, no extra watering' )
        logger.info('temperature forecasted ' + str(w.temp_today) + ' less than ' + str(min_temp_set))
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
    min_temp_set = [sys.argv[1] if len(sys.argv)>1 else 'min_temp_set1'][0]
    
    extra_time = extra_for_weather(p.water.extra_threshold, p.water.extra,p.water.was_raining, int(getattr(p.water,min_temp_set)))

    params = {1 : {'relay': p.pins.water1, 'motor' : p.pins.motor, 'time' : p.water.time1  + extra_time}, 
              2 : {'relay': p.pins.water2, 'motor' : p.pins.motor, 'time' : p.water.time2  + extra_time}} 
    water(params)