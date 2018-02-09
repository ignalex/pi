# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 07:38:54 2018

@author: Alexander Ignatov
"""
from __future__ import print_function
import os, sys

from modules.common import  LOGGER
logger = LOGGER('internet_speed', level = 'INFO')
from modules.common import Dirs, CONFIGURATION
from modules.postgres import PANDAS2POSTGRES
log = os.path.join(Dirs()['LOG'],'internet_speed.txt') # for data

from subprocess import Popen, PIPE
from time import sleep
#import urllib2
import speedtest
#from modules.speakPI4 import Speak #TODO: fix
import pandas as pd
import plotly
import cufflinks
import datetime


#%%
#def URL_authentication(url, login, password):
#    # create a password manager
#    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
#    # Add the username and password.
#    # If we knew the realm, we could use it instead of None.
#    password_mgr.add_password(None, url, login, password)
#    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
#    # create "opener" (OpenerDirector instance)
#    opener = urllib2.build_opener(handler)
#    # use the opener to fetch a URL
#    #opener.open(a_url)
#    return opener

#def Reboot(url = 'http://192.168.1.1/setup.cgi?todo=reboot', login = 'admin', password = 'admin'):
#    LOG( 'internet' , -1 ,'rebooting')
##    Speak("I can't ping google. I am going to reboot the internet.")
#    #URL_authentication(url, login, password).open(url)

#%%

#def LOG(prefix = '', msg = '', comment = '', stamp = True) :
#    'quick messaging module'
#    msg = '\t'.join([[str(datetime.datetime.now()).split('.')[0] if stamp else ''][0], str(prefix), str(msg), str(comment)])
#    print (msg, file=open(os.path.join(path, log),'a'))
#    logger.info(msg)


#class CheckInternet(object):
#    """IP - to ping
#    check = [times, delay]"""
#    def __init__ (self, IP = 'www.google.com', check = [4,30]):
#        self.IP, self.check = IP, check
#        if self.Ping() == False:
##            Reboot()
##            sleep(60)
#            logger.error('HERE I WOULD REBOOT tenda')
#            if self.Ping():
#                LOG('internet', 2, 'restarted - OK' )
#            else:
#                LOG('internet', -2, 'still no good' )
#        else:
#            LOG('internet', 1, 'OK' )
#    def Ping(self):
#        for n in range(0,self.check[0]):
#            logger.info('attempt ' + str(n))
#            if self.Ping_1(self.IP) == True: return True
#            sleep(self.check[1])
#        return False
#    def Ping_1(self,IP):
#        process = Popen(['ping -n 2 -w 1000' if os.name == 'nt' else 'sudo ping -w 2 -q' ][0].split(' ') + [self.IP], stdout=PIPE, stderr=PIPE)
#        stdout, stderr = process.communicate()
#        REPLIES  = {"100% loss" : False,
#                    '100% packet loss' : False,
#                    'Destination host unreachable' : False,
#                    "Average ="  : True ,
#                    ' 0% packet loss' : True}
#        try:
#            return [ v for k,v in REPLIES.items() if stdout.find(k) != -1][0]
#        except:
#            return None
#

#def SpeedTest_old(plot = True, copyToIndex = True):
#    s = speedtest.Speedtest()
#    s.get_best_server()
#    s.download()
#    s.upload()
#    s.results.share() #TODO: link to site
#
#    results_dict = s.results.dict()
#
#
#    LOG('speed_download' ,  results_dict['download']/(1024*1024))
#    LOG('speed_upload' ,  results_dict['upload']/(1024*1024))
#    LOG('speed_ping' ,  results_dict['ping'])
#
#    if plot:
#        plotting = PLOT()
#        # here apache must be installed sudo apt-get install apache2 -y [ https://www.raspberrypi.org/documentation/remote-access/web-server/apache.md ]
#        if copyToIndex: plotting.put_to_index_html('/var/www/html/internet_speed/index.html')

#%%
#class PLOT(object):
#    def __init__(self):
#        self.df = self.read_dataFrame()
#        self.get_plots(self.df)
#    def read_dataFrame(self):
#        df = pd.read_csv(log, sep = '\t', names = ['time', 'type', 'val', 'comment'], parse_dates=['time'], index_col = 'time')[[ 'type', 'val']]
#        speed = df[df['type'].isin( ['speed_download','speed_upload','speed_ping'])].pivot(columns = 'type', values = 'val').\
#                rename(columns = {'speed_up' : 'upload', 'speed_down' : 'download', 'speed_ping' : 'ping'}) #FIXME: error here
#        #speed = df[df['type'].str.startswith('speed') & ~df['type'].str.endswith('host')].pivot(columns = 'type', values = 'val').applymap(lambda x : np.float(x))
#        #ping = pd.DataFrame({'internet': df[df['type'] == 'internet'] }) #.val.apply(lambda x : {'OK' : 1, 'rebooting' : 0, 'restarted - OK' : 1, 'still no good' : 2}[x])})
#        #return speed.join(ping, how = 'outer').rename(columns = {'speed_up' : 'upload', 'speed_down' : 'download', 'speed_ping' : 'ping'})
#        return speed
#    def get_plots(self,df, plots = ['plot_last_3days','plot_ping']): #plot_speed
#        html = ['<head>' ]
#        divs = {}
#        for plot in plots:
#            divs[plot] = globals()[plot](df)
#            html += ['<br><b>' + plot + '</b><br>' + divs[plot]]
#        html += ['</html>']
#        print ( '\n'.join(html), file=open(os.path.join(path,'index.html'), 'w'))
#    def put_to_index_html(self,path_index):
#        try:
#            os.system('sudo cp ' + os.path.join(path,'index.html') + ' ' + path_index  )
#            os.remove(os.path.join(path,'index.html'))
#        except Exception as e:
#            logger.error( 'cant copy index.html >> ' + str(e))
#
#def plot_ping(df):
#    return plotly.offline.plot(change_plot(df['internet'].dropna().iplot(asFigure = True)),output_type = 'div',show_link = False,   include_plotlyjs = False)
##%%
#def plot_last_3days(df):
#    df['upload'], df['ping'] = - df['upload'], - df['ping']
#    last = df[['download','upload','ping']].dropna().truncate(df[['download','upload']].dropna().index.max() - pd.tseries.offsets.Day() * 20)#.resample('5T').mean().interpolate(method = 'cubic')
#    fig1 = last[['upload','download']].dropna().iplot(columns = ['upload','download'], width = [2,2],   fill = True, colors = ['green','blue'],  asFigure = True)
#    fig2 = last[['ping']].dropna().iplot(columns = ['ping'], secondary_y = ['ping'], kind = 'bar', colors = ['red'],   asFigure = True)
#    fig2['data'].extend(fig1['data'])
#    return plotly.offline.plot(change_plot(fig2), filename = os.path.join(path,'index.html'), output_type = 'div',show_link = False)
#
#def change_plot(div, layout = {'width' : '1000', 'height' : '350'}):
#    for k,v in layout.items():
#        div.layout[k] = v
#    return div

def SpeedTest():
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()
    s.results.share() #TODO: link to site

    results_dict = s.results.dict()
    sss = {k:v for k,v in results_dict.items() if k != 'server'}
    df = pd.DataFrame.from_dict(sss, orient='index').T
    return df

#%%
if __name__ == '__main__':
    args = sys.argv[1:]
    path = Dirs()['LOG']
    p = CONFIGURATION()
    con = PANDAS2POSTGRES(**p.hornet_pi_db)
    df = SpeedTest()
    con.write(df, 'internet_speed')
#    if '-speed' in args:
#        SpeedTest()
##    elif '-reboot' in args:
##        Reboot()
#    else:
#        CheckInternet('www.google.com',   [4,30] )
