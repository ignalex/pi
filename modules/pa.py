# -*- coding: utf-8 -*-
"""
integration with PA service 

Created on Sat Aug 02 08:04:03 2014
@author: ignalex
"""
 
import os,sys

#TODO: hardcoding out  
def pa(arg): 
    if type(arg) == list: arg = arg[0]
    path = [os.path.join(i, 'PA.py ') for i in [j for j in ['/home/pi/PYTHON/GPIO','/home/pi/git/pi'] if os.path.exists(j)][0]][0]
    os.system("sudo python " + path + arg + " &" )

if __name__ == '__main__': 
    arg = sys.argv[1]
    pa(arg)