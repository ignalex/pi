# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 07:38:54 2018

@author: Alexander Ignatov
"""
from __future__ import print_function
import sys

from modules.common import  LOGGER
logger = LOGGER('internet_speed', level = 'INFO')
from modules.common import CONFIGURATION
from modules.postgres import PANDAS2POSTGRES
from flask import Flask


import speedtest
#from modules.speakPI4 import Speak #TODO: fix
import pandas as pd
import plotly
import cufflinks
import datetime

p = CONFIGURATION()
app = Flask(__name__)

def try_to_float(a):
    try:
        return float(a)
    except:
        return a

def SpeedTest():
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()
    s.results.share()
    results_dict = s.results.dict()
    df = pd.DataFrame.from_dict( {k : try_to_float(v) for k, v in results_dict.items() if k not in ['server', 'timestamp']}, orient='index').T
    df ['timestamp'] = datetime.datetime.now()
    return df

def to_db(df):
    try:
        con = PANDAS2POSTGRES(p.hornet_pi_db.__dict__)
        con.write(df, 'internet_speed')
        return True
    except Exception as e:
        logger.error(str(e))

def read_data_from_db(last_days=5):
    con = PANDAS2POSTGRES(p.hornet_pi_db.__dict__)
    df = con.read("""select timestamp, extract(hour from timestamp) as hour,
	round (upload :: numeric / (1024 * 1024), 2)  as upload,
	round ( download :: numeric  / (1024 * 1024), 2)  as upload,
	upload :: numeric
	from internet_speed
    where now() - timestamp <= '{} days' """.format(last_days)) #TODO: limit last days
    return df

@app.route("/internet_speed")
def internet_speed():
    # line chart
    df = read_data_from_db()
    line = df[['upload', 'upload' ,'upload']].set_index('timestamp').resample('10min').interpolate('pchip')

    div1 = plotly.offline.plot(line.iplot(theme = 'solar', asFigure = True, title = 'internet speed'), output_type='div')
    div2 = plotly.offline.plot(df.pivot(columns = 'hour', values='download').iplot(kind = 'box', asFigure=True, boxpoints='all', theme='solar', legend=False), include_plotlyjs = False)
    return div1+div2#render_template('forecasting.html', plotly_mvp=div)
#TODO: templates / inject DIV.
#TODO: btn 'scan now'
#TODO: link to last scan

#%%
if __name__ == '__main__':
    args = sys.argv[1:]
    if '-speed' in args:
        status = to_db(SpeedTest())
        logger.info(str(status))
    elif '-flask' in args:
        app.run(debug=True, use_debugger = False, use_reloader = False, port = 8082, host = '0.0.0.0')
