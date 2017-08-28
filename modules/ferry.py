# -*- coding: utf-8 -*-
"""
Created on Wed Nov 04 06:44:44 2015

@author: ignalex
"""
from __future__ import print_function
import  datetime , os 
from common import Dirs

def NextFerry(): 
    "reyturns the time of the next ferry. timetable lives in 'data' directory"
    data = Dirs['DATA']
    DAY = ['' if datetime.datetime.today().weekday()<5 else ['_SAT' if datetime.datetime.today().weekday() else '_SUN' ][0]][0]
    timetable = open(os.path.join(data,'ferry'+DAY+'.txt'),'r').read().split('\n')
    lst = []
    for a in timetable: 
        lst.append(datetime.time(int(a.split(':')[0]),int(a.split(':')[1])))
    cut_off =  datetime.datetime.now() + datetime.timedelta(minutes = 5)
    nxt = [i for i in lst if i > datetime.time(cut_off.hour, cut_off.minute) ]
    if nxt == []: 
        return 'F--'
    else: 
        min_to_next = (datetime.datetime.combine(datetime.date.today(),nxt[0]) - datetime.datetime.now()).seconds/60
        if min_to_next > 99: 
            return 'F--'
        else: 
            return 'F'+str(min_to_next).zfill(2)
        
if __name__ == '__main__': 
    print (NextFerry()) 