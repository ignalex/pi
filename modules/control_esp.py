# -*- coding: utf-8 -*-
"""
API indterface to ESP modules

Created on Fri Oct 21 07:32:18 2016
@author: Alex
"""
import requests, sys, time, datetime, os
from joblib import Parallel, delayed
#TODO: change structure to use ESP-micropython returning json
#TODO: log state

import __main__ as m

def Request(com):
    "outside class for joblib"
    try:
        resp = requests.request('GET', com, timeout = 4).content.replace('<!DOCTYPE HTML>\r\n<html>\r\n', '').replace('</html>\n','')
        if type(resp) != str : resp = resp.decode("utf-8")
        if resp.find('high') != -1 :            return '1'
        if resp.find('low') != -1 :             return '0'
        if resp.find('alive') != -1 :           return 'OK'
        if resp.find('duplicated') != -1 :      return 'repeated request'
        if resp.isdigit():                      return resp
        if resp.find('no func ')      != -1 or \
           resp.lower().find('error') != -1 :   return 'error'
        if resp.find('command sent'):           return 'OK'
        return 'no dict found for ' + resp
    except:
        try:
            m.logger.info('error in ' + com + ' : ' + str(sys.exc_info()))
        except:
            pass
        return str(com[19]) + '-X'

class ESP(object):
    def __init__ (self, command = [], timeout = 4 , on_off_times = [5, 12]):
        self.sensor_history =  []
        self.timeout = timeout
        self.on_off_times = on_off_times
        self.status_onoff = 1 # starting from open
        self.parallel = False
        self.sensor_log = '/home/pi/LOG/light_sensor.txt'
        if command != []: self.Go(command)
    def Go(self, command = ['alive','12356'], base = 170):
        #TODO: rewire 175 > to accept 'gpio'
        """ communicate with ESP module
        command = [what, list_devs]               - old format : http://IP/gpio/1
        command = [list_devs {last digits}, function, command]  - new format : http://IP/command/light/on
        """
        self.result, self.status, self.raw = [], [], []
        if len(command) == 2: # old format
            if command[0].lower() == 'alive': command[0] = 'are_you_alive' #FIXME: for 176
            self.devices = ['http://192.168.1.' + str(base + int(i)) + '/gpio/' + command[0] for  i in list(command[1])]
        elif len(command) >= 3: # new format  # e.Go(['6','rf433','3','0']) !!! IP is 1st
            list_devs, function, commands = list(command[0]), command[1], command[2:]
            self.devices = ['http://192.168.1.' + str(base + int(i)) + '/' + '/'.join(['control', function, '/'.join(commands)]) for  i in list_devs]
            m.logger.warn(str(self.devices))
        else:
            m.logger.warn('unknown format of command')
            return
        # triggering all commands to all devices
        if not self.parallel:
            for dev in self.devices:
                self.result.append(str(dev[19]) + ' - ' + Request(dev))
        else: # parallel
            self.result = [ str(i) for i in Parallel(n_jobs=3)(delayed(Request)(dev) for dev in self.devices)]
        m.logger.warn('\t'.join([i for i in self.result if i is not None]))
#        self.stats()
#    def stats(self, file_name = [os.path.join(i, 'esp_alive.txt') for i in ['/home/pi/LOG/',os.getcwd()]  if os.path.exists(i)][0]):
#        print >> open(file_name,'a'), '\n'.join([str(datetime.datetime.now()).split('.')[0] + '\t' + i.split('-')[0] + '\t'+ \
#                      ['1' if j == 'OK' else '0' for j in [i.split('-')[1]]][0]   for i in self.result if i is not None])
    def Go_parallel(self,command = ['alive','12356']):
        self.parallel = True
        self.Go(command)
        self.parallel = False

#    def Light_Sensor(self):
#        self.Go(['sensor', '3'])
#        try:
#            print >> open(self.sensor_log,'a'), str(datetime.datetime.now()).split('.')[0] + '\t' + str(self.result[-1].split(' - ')[-1])
#        except:
#            pass #
#        try:
#            self.sensor_history.append(int(self.result[-1].split(' - ')[-1]))
#            return self.sensor_history[-1]
#        except:
#            return False

#    def Last_readings_more(self ): # last N readings > thrushold - T / F
#        return len([i for i in self.sensor_history[- self.thresholds['count']:] if i >= self.thresholds['up']]) == self.thresholds['count']
#    def Last_readings_less(self ): # last N readings < thrushold - T / F
#        return len([i for i in self.sensor_history[- self.thresholds['count']:] if i <= self.thresholds['down']]) == self.thresholds['count']

#    def Decide_On_Off(self, thresholds = {'count' : 3, 'up' : 500,'down' : 450} ):
#        self.thresholds = thresholds
#        self.Light_Sensor() # getting new readings
#        if not (datetime.datetime.now().hour >= self.on_off_times[0] and datetime.datetime.now().hour <= self.on_off_times[1]):
#            m.logger.debug('time outside watching window')
#            return
#        else:
#            m.logger.debug('time inside window')
#            if self.Last_readings_more() and self.status_onoff == 1:
#                m.logger.debug('off based on last readings ' + str(self.sensor_history[-5:]) )
#                self.Go(['0','23'])
#                self.status_onoff -= 1
#                try:
#                    os.system('sudo python /home/pi/PYTHON/GPIO/PA.py ' + '"blindes down"')
#                except:
#                    pass
#            if self.Last_readings_less() and self.status_onoff == 0:
#                m.logger.debug('on based on last readings ' + str(self.sensor_history[-5:]) )
#                self.Go(['1','23'])
#                self.status_onoff += 1
#                try:
#                    os.system('sudo python /home/pi/PYTHON/GPIO/PA.py ' + '"blindes up"')
#                except:
#                    pass
#    def Sensor_Loop(self, loop_delay = 1):
#        'loop sensor'
#        while True:
#            self.Light_Sensor()
#            try:
#                m.logger.debug( '\tsensor\t' + str(self.result[-1]))
#            except:
#                pass
#            time.sleep(loop_delay)

#    def Plot(self):
#        self.df = pd.read_csv(self.sensor_log,sep = '\t', names=['date','val'], index_col='date', parse_dates=True)
#
#

if __name__ == '__main__':
    from common import LOGGER #, FAKE as OBJECT
#    m = OBJECT()
#    m.logger = LOGGER('esp.txt', level = 'INFO')
    logger = LOGGER('esp.txt', level = 'LOG')

    e = ESP()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'sensor':
#            e.Sensor_Loop(loop_delay = 5)
            pass
#    e.Go_parallel( )
#    e.Light_Sensor( )
    #e.Go(['6','rf433','all','off'])
    ##
    # 1. integrate into plot
    # 2. clean logic
    # on off logic > if its morning and light > ... >> off