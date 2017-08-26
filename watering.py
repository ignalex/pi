# -*- coding: utf-8 -*-
"""watering module / updated
* to be run under sudo """

import sys 
from modules.relay import cascade 
#TODO: fix #from modules.talk import Speak
from modules.weather import WEATHER

def extra_for_weather(threshhold = 20, extra =  2): 
    w = WEATHER(False)
    w.ToInt()

    if w.WasRaining(): 
#        Speak('it was raining for '+ str(w.rain) + ' mm yesterday. I will not water the plants' )
        sys.exit()
    
    result = [(w.temp_today - threshhold) * extra if (w.temp_today - threshhold) > 0 else 0][0] 
#    Speak('temperature forecasted ' + str(w.temp_today) + ' degrees. adding ' + str(result) + ' seconds for watering')       
    return result 
  
   
def water(params):     
    "main triggering"
    for n, config in params.items():         
        cascade([config['relay'],config['motor']], 1, config['time'] )


#%%
if __name__ == '__main__': 
   
    extra_time = extra_for_weather()
    params = {1 : {'relay': 2, 'motor' : 1, 'time' : 20  + extra_time}, 
              2 : {'relay': 3, 'motor' : 1, 'time' : 30  + extra_time}} 
    water(params)