# -*- coding: utf-8 -*-
"""
place info on the LCD panel, controlled by arduino
* communication via serial 
* to be started via crontab on @reboot 

current info: 
  - weather forecast 
  - next ferry 
  - temperature outside: 
    current / maximum expecned 
  - temperature inside 
  - time 

Created on Thu Oct 29 07:12:47 2015
@author: ignalex
"""
from __future__ import print_function

import daemon 
import serial, os, sys 
sys.path.append('/home/pi/git/pi/') #needed if started from crontab 
from datetime import datetime , timedelta
from time import sleep
from modules.weather import WEATHER
from modules.ferry import NextFerry
from modules.lock import LockArd as Lock
#TODO: fix #from modules.SHELL import PID

class LCD(object): 
    def __init__(self,DEBUG = False): 
        self.DEBUG = DEBUG 
        self.ser = self.FindSerialPort()

    def FindSerialPort(self,wait=1): # less than 1 not enough to prepare serial port 
        if os.name == 'posix': # Linux 
            port = [i for i in os.listdir('/dev') if i.startswith('ttyACM')][0]
            if self.DEBUG: print (os.path.join('/dev',port))
            ser =  serial.Serial(os.path.join('/dev',port))
        else: 
            ser =  serial.Serial('COM6', 9600, timeout=0) #windows integration > to be depricated       
        sleep(wait)
        return ser    
    def PrintPos(self,pos ,text): 
        position = str(pos[0])+str(self.TranslatePosition(pos[1])) 
        send_string =  'P' + position + text
        if self.DEBUG: print (pos, send_string)
        with Lock('serial'): self.ser.write(send_string)
    def Print(self,text): 
        with Lock('serial'): self.ser.write('P00' + text)
    def TranslatePosition(self,pos): 
        dictionary = {10:':', 11 : ';', 12 : '<', 13 : '=', 14 : '>', 15 : '?'}
        if pos < 9: return pos
        else: return dictionary[pos]
    def Clean(self): 
        with Lock('serial'): self.ser.write('C')
    def Time(self): 
        now = str(datetime.now()).split('.')[0].split(' ')[1][:-3]
        with Lock('serial'): self.ser.write('T'+now)
        self.last_min = datetime.now().minute
    def LightSensor(self,wait = 0.2): 
        count = 0
        while count < 10: 
            with Lock('serial'): 
                self.ser.write('S')
                sleep(wait)
                read =  self.ser.readline().replace('\r\n','')
                if len(read) > 3 or int(read) > 255 or int(read) < 50:  # > 255 - bullshit, < 100 - outlier 
                    count +=1
                else: 
                    return read 
        return 'NaN'

def PrintWeather(lcd): 
    global print_weather
    w = WEATHER()
    if not w.timeout: 
        lcd.PrintPos((1,0),str(int(w.temp_out)).zfill(2) + '/'+  str(int(w.temp_today)).zfill(2))
        sleep(1)    
        lcd.Print(w.forecast[:14].ljust(14)+str(w.temp_in).ljust(2))
    print_weather = datetime.now()

def PrintNextFerry(lcd):
    sleep(1)    
    lcd.PrintPos((1,6),NextFerry()+'  ')

def LightSensor(lcd): 
    print (lcd.LightSensor())
    
def Start(): 
    global lcd 
#    PID()
    lcd = LCD()  
    lcd.Clean()
    lcd.Time()
    sleep(1)
    PrintWeather(lcd)
    PrintNextFerry(lcd)
    lost = False
    print_weather = datetime.now() - timedelta(seconds = 130)
    
    while True: 
        try: 
            if datetime.now().minute == 59 and datetime.now().second > 57: # clean screen 
                lcd.Clean()
            if lcd.last_min != datetime.now().minute or lost: # time / ferry 
                lcd.Time()
                sleep(1)
                PrintNextFerry(lcd)
                lost = False
            if (datetime.now().minute%5 == 0 and datetime.now().second < 10) and (datetime.now() - print_weather).seconds > 120: 
                sleep(1)                
                PrintWeather(lcd) 
            sleep(1)    
            
        except: # if connection to serail lost - it can be reassigned the port 
            try: 
                lcd = LCD()
                lost = True
            except: 
                sleep(5)
#        sys.exit()
            
if __name__ == '__main__': 
    with daemon.DaemonContext():
        Start()
