# -*- coding: utf-8 -*-
"""
common used functions 


Created on Sun Aug 27 07:02:30 2017
@author: Alexander Ignatov
"""
from __future__ import print_function
import os

class GROUPED_PARAMS(object): 
    def __init__(self,ini_files=[]):
        ini_files = ['config'] + ini_files #adding config default 
        self.data_path = [i for i in ['/home/pi/git/pi/data',os.getcwd()] if os.path.exists(i) == True][0] 
        self.INI = {}
        for ini_file in [i+'.ini' for i in ini_files]: 
            if os.path.exists(os.path.join(self.data_path,ini_file)): 
                self.INI.update(self.ReadIniByGroup(ini_file))
        for k,p in  self.INI.items(): setattr(self, k, self.DictParams(p))
        self.debug_file_list = []
        for p in [k for k,v in self.INI.items() if v in ['YES','NO']]: setattr(self, p, [True if i == 'YES' else False for i in [self.INI[p]]][0])
        self.ReplaceKeys()
    def ReadIniByGroup(self,filename):
        try: 
            INI_file = open(os.path.join(self.data_path,filename),'r').read().splitlines()
        except: 
            print ('cant open ' + filename)
        INI_file = [i for i in INI_file if len(i) != 0] # empty strings 
        INI_file = [i for i in INI_file if i[0] != '#'] 
        param = {}
        try: 
            for ini in INI_file.replace(' := ',' = '): 
              param[ini.split()[0]] = ini.split(' = ')[1].split('#')[0]
        except: 
            print ('error parsing')
        return param
    def DictParams(self,p): 
        if p.find('|') == -1: 
            return FixValues(p)
        else: 
            d = OBJECT()
            for pair in p.split(','): setattr(d, self.CheckIfDate(pair.split('|')[0]) , FixValues(pair.split('|')[1]))
            return d
    def ReplaceKeys(self): 
        for key in self.__dict__.keys(): 
            if type(getattr(self,key)) == dict: 
                parsed = {}
                for k,v in getattr(self,key).items(): 
                    if v in self.__dict__.keys(): 
                        parsed[k] = getattr(self,v)
                    else: 
                        parsed[k] = v
                setattr(self,key,parsed)

    def CheckIfDate(self,left_of_pair): 
        if left_of_pair.replace('.','').isdigit(): 
            return 'DATE_'+left_of_pair.replace('.','_')
        else: 
            return left_of_pair
          
class OBJECT (object): 
    def __init__(self): 
        pass 

def FixValues(v): # in calibrating - fixing strings into lists of int/floats 
    if v.find(';') != -1: 
        return [TryToInt(i) for i in v.split(';')]
    else: 
        return  TryToInt(v)

def TryToInt(a): 
    try: 
        if float(a) == int(a): 
            return int(a)
    except: 
        try: 
            return float(a)
        except: 
            return a   