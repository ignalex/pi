"""
temperature sensor set up - read https://core-electronics.com.au/tutorials/temperature-sensing-with-raspberry_pi.html
"""
from __future__ import print_function
import os 

def Temp():    
    "get temp from w1" 
    IDs = ['28-000005e77734','28-000005e73eb5']
    try:     
        path = ['/sys/bus/w1/devices/__ID__/'.replace('__ID__',i) for i in IDs if os.path.exists('/sys/bus/w1/devices/__ID__/'.replace('__ID__',i))]
        if path == []: 
            os.system('sudo modprobe w1-gpio')
            os.system('sudo modprobe w1-therm')
            print ('modprobe w1-gpio and w1-therm started')
            path = ['/sys/bus/w1/devices/__ID__/'.replace('__ID__',i) for i in IDs if os.path.exists('/sys/bus/w1/devices/__ID__/'.replace('__ID__',i))]
        st = round((float(os.popen('cat '+path[0]+'w1_slave').read()[-6:-1])/1000),2)
        return st
    except: 
        return False

if __name__ == '__main__': 
    print (Temp())