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
#DONE: fix #from modules.SHELL import PID
#DONE: fix hanging (blank screen)
#DONE: logging

from __future__ import print_function

import daemon
import serial, os, sys
sys.path.append('/home/pi/git/pi/') #needed if started from crontab
from datetime import datetime , timedelta
from time import sleep
from modules.common import  LOGGER, PID, MainException
from modules.weatherzone import WEATHER
from modules.ferry import NextFerry
from modules.lock import LockArd as Lock

class LCD(object):
    def __init__(self,DEBUG = False):
        self.DEBUG = DEBUG
        self.ser = self.FindSerialPort()

    def FindSerialPort(self,wait=1): # less than 1 not enough to prepare serial port
        if os.name == 'posix': # Linux
            port = [i for i in os.listdir('/dev') if i.startswith('ttyACM')][0]
            logger.debug (os.path.join('/dev',port))
            ser =  serial.Serial(os.path.join('/dev',port))
        else:
            ser =  serial.Serial('COM6', 9600, timeout=0) #windows integration > to be depricated
        sleep(wait)
        return ser
    def PrintPos(self,pos ,text):
        position = str(pos[0])+str(self.TranslatePosition(pos[1]))
        send_string =  'P' + position + text
        logger.debug (str(pos) + send_string)
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
#    def LightSensor(self,wait = 0.2): #not used
#        count = 0
#        while count < 10:
#            with Lock('serial'):
#                self.ser.write('S')
#                sleep(wait)
#                read =  self.ser.readline().replace('\r\n','')
#                if len(read) > 3 or int(read) > 255 or int(read) < 50:  # > 255 - bullshit, < 100 - outlier
#                    count +=1
#                else:
#                    return read
#        return 'NaN'

def PrintWeather(lcd):
    global print_weather
    try:
        w = WEATHER()
        if not w.timeout:
            lcd.PrintPos((1,0),str(int(w.temp_out)).zfill(2) + '/'+  str(int(w.temp_today)).zfill(2))
            sleep(1)
            lcd.Print(w.forecast[:14].ljust(14)+str(w.temp_in).ljust(2))
        else:
            logger.error('timeout reading weather')
        print_weather = datetime.now()
    except:
        logger.error('error in weather module')

def PrintNextFerry(lcd):
    sleep(1)
    lcd.PrintPos((1,6),NextFerry()+'  ')

#def LightSensor(lcd):
#    logger.info(lcd.LightSensor())

logger = LOGGER('lcd', level = 'INFO')

def Start():
    global lcd
    PID()
    lcd = LCD()
    lcd.Clean()
    lcd.Time()
    sleep(1)
    PrintWeather(lcd)
    PrintNextFerry(lcd)
    lost = False
    attempt = 1
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
            attempt = 1

        except: # if connection to serail lost - it can be reassigned the port
            try:
                lcd = LCD()
                lost = True
            except Exception as e:
                attempt += 1
                if attempt > 5:
                    logger.fatal(str(e))
                    return
                logger.error('attempt' + str(attempt) + ' ' + str(e))
                sleep(5)
#        sys.exit()

if __name__ == '__main__':
    with daemon.DaemonContext(files_preserve = [logger.handlers[0].stream,]):
        try:
            Start()
        except:
            MainException()
