#!/usr/bin/python
"""
for sydney for today returns

[sunrise,sunset,window_light,total_dark,sun_has_gone]
* window_light is my specific parameter, just disregard it ...
* using table in 'data' folder

Created on Wed Apr 30 15:43:41 2014

@author: aignatov
"""
from __future__ import print_function
try:
    from common import Dirs
except:
    from modules.common import Dirs
import datetime, os

# from astral import LocationInfo
# from astral.sun import sun

def Sun(date, filename = 'sunrise2014.txt'):
    "gets the date, returns tuple with [sunrise,sunset,window_light,total_dark]"
    shift_hours = [6,9] # for window light and sun has gone
    file_path = os.path.join(Dirs()['DATA'], filename)
    dates = open(file_path,'r').read().split('\n')[1:]
    string = [i for i in dates if int(i.split(' ')[0]) == date.month and int(i.split(' ')[1]) == date.day ][0]
    twilight = [string.split(' ')[5],string.split(' ')[6], string.split(' ')[7]]
    today = datetime.date.today()
    sunrise = datetime.datetime(today.year, today.month, today.day, int(twilight[0].split(':')[0]), int(twilight[0].split(':')[1]),0)
    sunset = datetime.datetime(today.year, today.month, today.day, int(twilight[1].split(':')[0]), int(twilight[1].split(':')[1]),0)
    window_light = datetime.datetime(today.year, today.month, today.day, int(twilight[0].split(':')[0]) + shift_hours[0], int(twilight[0].split(':')[1]),0)
    total_dark = datetime.datetime(today.year, today.month, today.day, int(twilight[2].split(':')[0]), int(twilight[2].split(':')[1]),0)
    sun_has_gone = datetime.datetime(today.year, today.month, today.day, int(twilight[0].split(':')[0]) + shift_hours[1], int(twilight[0].split(':')[1]),0)

    dawn = datetime.datetime(today.year, today.month, today.day, int(string.split(' ')[4].split(':')[0]), int(string.split(' ')[4].split(':')[1]),0)

    return [sunrise,sunset,window_light,total_dark,sun_has_gone,dawn]

def IsItNowTimeOfTheDay(the_type):
    sun = Sun(datetime.date.today())["sunrise,sunset,window_light,total_dark,sun_has_gone".split(',').index(the_type)]
    return  sun.hour == datetime.datetime.now().hour and sun.minute == datetime.datetime.now().minute


# def Astro():
#     today = datetime.date.today()
#     city = LocationInfo("Sydney", "Australia", "Australia/Sydney", -33.8688, 151.2093)
#     s = {j:  datetime.datetime(today.year, today.month, today.day, i.hour, i.minute,0)  for j,i in
#          {k : v.astimezone() for k, v in sun(city.observer, date=datetime.date.today()).items()}.items()}
#     return  s

if __name__ == '__main__':
    for a in Sun(datetime.date.today()):
        print (str(a))