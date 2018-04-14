# -*- coding: utf-8 -*-
"""
common used functions


Created on Sun Aug 27 07:02:30 2017
@author: Alexander Ignatov
"""
#DONE: hvae 2 configs > 1 in data, 1 in git (for specific params)
#DONE: think how to read from right config while having them controlled by GIT  (socket.gethostname() ? )

from __future__ import print_function
import os, sys, logging, argparse, traceback, datetime
from subprocess import Popen, PIPE
import socket
import __main__ as m

def Dirs():
    return {'LOG' : [i for i in ['/home/pi/LOG/', '/home/pi/temp/', r'C:\_LOG', '/Users/s84004/temp', os.getcwd()] if os.path.exists(i)][0],
            'DATA': [i for i in ['/home/pi/git/pi/data', '../data/', '/Users/s84004/Dropbox/GIT/ignalex/pi/data/', '/home/pi/temp/',  os.getcwd()] if os.path.exists(i)][0],
            'REPO': [i for i in ['/home/pi/git/pi', '../../'] if os.path.exists(i)][0]
            }

class CONFIGURATION(object):
    """read config:
        1. [hostname].ini file located in DATA dir
        2. config.ini file located in DATA dir
        3. files passed as arguments to the function
        4. config.ini file located 1 level above any repo (secure - to be outside GIT)
        parsing and returning object with attribs"""
    def __init__(self,ini_files=[]):
        self.hostname = socket.gethostname()
        self.INI_FILES = [os.path.join(Dirs()['DATA'], i + '.ini') for i in [self.hostname, 'config'] if os.path.exists(os.path.join(Dirs()['DATA'], i + '.ini'))] + \
                         [os.path.join(os.getcwd(), i + '.ini') for i in ini_files] + \
                         [i for i in [os.path.join(os.path.split(Dirs()['REPO'])[0], 'config.ini')] if os.path.exists(i)] + \
                         [i for i in [os.path.join(os.path.split(os.getcwd())[0], 'config.ini')] if os.path.exists(i)]
        self.INI = {}
        for ini_file in self.INI_FILES:
            if os.path.exists(ini_file):
                self.INI.update(self.ReadIniByGroup(ini_file))
        for k,p in  self.INI.items(): setattr(self, k, self.DictParams(p))
#        self.debug_file_list = [] - not used

        #parsing 1st level of attribs
        for p in [k for k,v in self.INI.items() if v in ['YES','NO']]:
            setattr(self, p, [True if i == 'YES' else False for i in [self.INI[p]]][0])

#        self.ReplaceKeys()
    def ReadIniByGroup(self,filename):
        try:
            INI_file = open(filename,'r').read().splitlines()
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
        if p.find('|') == -1: # direct value, not a a parameter
            return self.FixValues(p)
        else:
            d = OBJECT()
            for pair in p.split(','):
                setattr(d, self.CheckIfDate(pair.split('|')[0]) , self.ParseYesNo(self.FixValues(pair.split('|')[1])))
            return d
    def ParseYesNo(self,val):
        if val in ['YES', 'NO']:    return [True if val == 'YES' else False][0]
        else:                       return val

    def CheckIfDate(self,left_of_pair):
        if left_of_pair.replace('.','').isdigit():
            return 'DATE_'+left_of_pair.replace('.','_')
        else:
            return left_of_pair

    def FixValues(self,v): # in calibrating - fixing strings into lists of int/floats
        if v.find(';') != -1:
            return [TryToInt(i) for i in v.split(';')]
        else:
            return  TryToInt(v)
#    def ReplaceKeys(self): # LOOKS UPUSED > for keys as DICTS, but now use attributes
#        for key in self.__dict__.keys():
#            if type(getattr(self,key)) == dict:
#                parsed = {}
#                for k,v in getattr(self,key).items():
#                    if v in self.__dict__.keys():
#                        parsed[k] = getattr(self,v)
#                    else:
#                        parsed[k] = v
#                setattr(self,key,parsed)


class OBJECT (object):
    "basic empty object"
    def __init__(self):
        pass


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

    #TODO: DB logging
    log_file =  os.path.join(Dirs()['LOG'], filename)
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
    try:
        m.logger.error(sys.argv[0].split('\\')[-1] + ' ['+ m.__doc__.split('\n')[-2].split(' ')[0] + ']')
    except:
        pass
    m.logger.error('ERROR REPORTED:'  )
    m.logger.error('TYPE: '+str(exc_type)+ ' : ' )
    m.logger.error("MESSAGE: "+ str(exc_value) )
    m.logger.error("TRACEBACK:")
    for frame in traceback.extract_tb(sys.exc_info()[2]):
        fname,lineno,fn,text = frame
        m.logger.error( "in line " + str(lineno) + " :  " + text)

def PID(onoff = '+' ,message = ''):
    """logging the system PID into HOME directory"""
    # need to handle different HOME dir for root and pi user...
    print ( '\t'.join( [str(datetime.datetime.now()).split('.')[0], str(os.getpid()), onoff,'\t'.join(sys.argv), message]),
           file = open(os.path.join(Dirs()['LOG'], 'pid.log'),'a'))

def LastLine(file_to_read, lines = 1):
    return Popen(("tail -{} ".format(lines) +  file_to_read).split(' '), stdout=PIPE, stderr=PIPE).communicate()[0]
