#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 08:35:21 2018

@author: s84004
"""

from weather import Weather
#from googletrans import Translator


class weather_yahoo():
    def __init__(self,name='kislovodsk'):
        self.name = name
        l = Weather().lookup_by_location(name)
        self.retrieved = l

        self.params = dict(
            now_temp = l.condition.temp,
            now_text = l.condition.text,

            today_high = l.forecast[0].high,
            today_low = l.forecast[0].low,
            today_text = l.forecast[0].text,
            today_wind = l.wind.speed.split('.')[0],

            today_sunrise = l.astronomy['sunrise'].replace(':',' '),
            today_sunset = l.astronomy['sunset'].replace(':',' '),

            tomorrow_high = l.forecast[1].high,
            tomorrow_low = l.forecast[1].low,
            tomorrow_text = l.forecast[1].text
            )

        self.start = 'weather forecast for ' + name
        self.today = 'temperature today from {today_low} to {today_high}, {now_text}, wind {today_wind} km per hr'.format(**self.params)
        self.sunrise = 'sunrise {today_sunrise}, sunset {today_sunset}'.format(**self.params)
        self.tomorrow = 'tomorrow temperature from {tomorrow_low} to {tomorrow_high}, {tomorrow_text}'.format(**self.params)
        self.all = '\n'.join([self.start, self.today, self.sunrise, self.tomorrow])

        print (self.all)


if __name__ == '__main__':
    WEATHER = weather_yahoo('kislovodsk')