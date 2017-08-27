# -*- coding: utf-8 -*-
"""
common used functions 


Created on Sun Aug 27 07:02:30 2017
@author: Alexander Ignatov
"""
from __future__ import print_function
import os, sys, logging, argparse, traceback, datetime
import __main__ as m 

#TODO: hvae 2 configs > 1 in data, 1 in git (for specific params)
class CONFIGURATION(object): 
    "read config file located in DATA dir, parsing and returning object with attribs" 
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
            for ini in INI_file: 
              param[ini.replace(' := ',' = ').split()[0]] = ini.replace(' := ',' = ').split(' = ')[1].split('#')[0]
        except: 
            print ('error parsing\n' + str(sys.exc_info()))
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
    "basic empty object" 
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

def arg_parser(): 
    "parsing command line args" 
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,)
       # default=logging.WARNING,)
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,)
    args, unknown = parser.parse_known_args()    
    return args 
          
def LOGGER(filename = r'log_filename.txt', level = 'INFO', verbose = False) :
    """generic logger class. Can handle different (changed) levels of verbosity (DEBUG, ERROR, INFO etc)
    IN: filename, level (from logging levels), verbose {True / False} - to catch info of where log printed from 
    OUT logger object"""
    # for iPython 
    logging.addLevelName(25,'LOG') # more than INFO, less than WARNING 
    logger = logging.getLogger()
    while len(logger.handlers): logger.removeHandler(logger.handlers[0])
    logger = logging.getLogger()

    if verbose: 
        formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s -  %(levelname)s - %(message)s',datefmt='%m-%d-%Y %I:%M:%S %p' )
    else: 
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',datefmt='%m-%d-%Y %I:%M:%S %p' )
    
    #TODO: log folder 
    #TODO: DB logging 
    log_file =  ([os.path.join(i,filename) for i in ['/home/pi/LOG','C:\_LOG'] if os.path.exists(i)] + [filename] )[0]
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)    
    logger.addHandler(ch)

    loglevel = [i for i in  [arg_parser().loglevel, level] if not i is None][0] # command line arg overrides what is in the script
    logger.setLevel(loglevel) #getattr(logging, level))
    logger.propagate = False
    return logger          
  
def MainException(): 
    "logger must be created in the main module with the name 'log'" 
    exc_type, exc_value, exc_traceback = sys.exc_info()
    m.log('\n------------------') #FIXME: use lg, log or logger
    try: 
        m.log(sys.argv[0].split('\\')[-1] + ' ['+ m.__doc__.split('\n')[-2].split(' ')[0] + ']')
    except: 
        pass 
    m.log('ERROR REPORTED:'  )   
    m.log('TYPE: '+str(exc_type)+ ' : ' )
    m.log("MESSAGE: "+ str(exc_value) )   
    m.log("TRACEBACK:")  

    for frame in traceback.extract_tb(sys.exc_info()[2]):
        fname,lineno,fn,text = frame
        m.log( "in line " + str(lineno) + " :  " + text)

def PID(onoff = '+' ,message = ''):
    """logging the system PID into HOME directory"""
    # need to handle different HOME dir for root and pi user... 
    path = [i for i in ['/home/pi',os.getcwd()] if os.path.exists(i)][0]
    print ( '\t'.join( [str(datetime.datetime.now()).split('.')[0], str(os.getpid()), onoff,'\t'.join(sys.argv), message]), 
           file = open(os.path.join(path, 'pid.log'),'a'))
  