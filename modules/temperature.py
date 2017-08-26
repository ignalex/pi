"""
temperature sensor set up - read https://core-electronics.com.au/tutorials/temperature-sensing-with-raspberry_pi.html
"""

from __future__ import print_function

import os#, subprocess
import __main__ as m 
import datetime 
from time import sleep 

def Temp():    
    "get temp from w1" 
    IDs = ['28-000005e77734','28-000005e73eb5']
    
    try:     
        path = ['/sys/bus/w1/devices/__ID__/'.replace('__ID__',i) for i in IDs if os.path.exists('/sys/bus/w1/devices/__ID__/'.replace('__ID__',i))]
        if path == []: 
            os.system('sudo modprobe w1-gpio')
            os.system('sudo modprobe w1-therm')
            print ('modprobe w1-gpio and w1-therm started')
            path = ['/sys/bus/w1/devices/__ID__/'.replace('__ID__',i) for i in IDs if os.path.exists('/sys/bus/w1/devices/__ID__/'.replace('__ID__',i))][0]
        st = round((float(os.popen('cat '+path[0]+'w1_slave').read()[-6:-1])/1000),2)
        return st
    except: 
        return False

#%% DEPRICATED  
def TempHumidAda(PiPin):
    output = os.popen('sudo ~/PYTHON/Adafruit-Raspberry-Pi-Python-Code/Adafruit_DHT_Driver/Adafruit_DHT 11 '+str(PiPin)).read()
    return output 

def TempHumidDHT(PiPin):
	try: 
		import dhtreader
		dhtreader.init()
		return dhtreader.read(11, PiPin)
	except: 
		return False

def CheckTempCondition (condition, sensor_range, hold = False):
    temp = float(Temp())
    m.log('current TEMP = ' + str(temp) )
    if condition == '<' : 
        if temp < int(sensor_range) and hold == False: 
            m.log('temp < ' + sensor_range + ' : TRIGGERING HEATER')
            return True 
        elif temp < int(sensor_range) and hold != False:
            now = datetime.datetime.now()
            force_stop_time = now + datetime.timedelta(float(hold)/24)
            count = 0
            while datetime.datetime.now() < force_stop_time: 
                temp = float(Temp())
                if temp >= int(sensor_range): 
                    m.log('TEMP increased to ' + str(temp) + ' : stopping heater')
                    break
                sleep(1)
                count +=1
                if count == 5: 
                    m.log('temp = ' + str(temp))
                    count = 0 
            if temp <= int(sensor_range) and datetime.datetime.now() >= force_stop_time: 
                m.log('temp is still ' + str(temp) + ' but MAX allowed time '+str(round(float(hold)*60,1))+' min for heater expired')
            elif temp >= int(sensor_range): 
                m.log('temp = ' + str(temp) + ' reached its highest range of ' + sensor_range)
            return False 
            
        else: 
            m.log(' > ' + sensor_range + ' : no heating needed')
            return False
    else: 
        m.log(' other conditions than "<" is not yet programmed.')
        return False        
                
            