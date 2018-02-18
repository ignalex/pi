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
from flask import Flask, render_template
from pandas_highcharts import core as phch_core
import json

try:
    import speedtest
except Exception as e:
    logger.error(str(e))
#from modules.speakPI4 import Speak #TODO: fix
import pandas as pd
import plotly
import cufflinks
import datetime

p = CONFIGURATION()

try:
    from flask_compress import Compress
    compress = Compress()

    def start_app():
        app = Flask(__name__)
        compress.init_app(app)
        return app
    app = start_app()
except:
    logger.info ('no compress used')
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
        logger.info('df added to DB')

        div = internet_speed()
        con.write(pd.DataFrame.from_dict({'current' : div}, orient='index').T, 'internet_speed_current', if_exists='replace')
        logger.info('text added to DB')

        return True
    except Exception as e:
        logger.error(str(e))

def read_data_from_db(last_days=5):
    con = PANDAS2POSTGRES(p.hornet_pi_db.__dict__)
    df = con.read("""select timestamp, extract(hour from timestamp) as hour,
	round (upload :: numeric / (1024 * 1024), 2)  as upload,
	round ( download :: numeric  / (1024 * 1024), 2)  as download,
	ping :: numeric
	from internet_speed
    where now() - timestamp <= '{} days' """.format(last_days)) #DONE: limit last days
    return df

def read_div_from_db():
    con = PANDAS2POSTGRES(p.hornet_pi_db.__dict__)
    df = con.read("""select current from internet_speed_current""")['current']#[0]
    last_scan = con.read("""select split_part(timestamp :: text, '.', 1) as datetime, extract('minutes' from now() - timestamp) :: int as minutes,  share from internet_speed where timestamp = (select max(timestamp) from internet_speed) """).T.to_dict()[0]
    return (df, last_scan)

@app.route("/internet_speed_live_process")
def internet_speed():
    # line chart
    df = read_data_from_db()
    line = df[['upload', 'download' ,'ping','timestamp']].set_index('timestamp')#.resample('20min').interpolate('pchip') # interpolation doesn't work on surface but OK on hornet :) starange

    DIVS = dict(
         div1 = plotly.offline.plot(line.iplot(theme = 'solar', asFigure = True, title = 'internet speed'), output_type='div', include_plotlyjs = False)
        ,div2 = plotly.offline.plot(df[['download', 'hour']].reset_index().pivot(columns = 'hour', values='download', index='index').iplot(title = 'download', kind = 'box', asFigure=True, boxpoints='all', theme='solar', legend=False),  output_type='div',include_plotlyjs = False)
        ,div3 = plotly.offline.plot(df[['upload', 'hour']].reset_index().pivot(columns = 'hour', values='upload', index='index').iplot(title = 'upload', kind = 'box', asFigure=True, boxpoints='all', theme='solar', legend=False),  output_type='div',include_plotlyjs = False)
        ,div4 = plotly.offline.plot(df[['ping', 'hour']].reset_index().pivot(columns = 'hour', values='ping', index='index').iplot(title = 'ping', kind = 'box', asFigure=True, boxpoints='all', theme='solar', legend=False),  output_type='div',include_plotlyjs = False)
    )
    return DIVS # saving dict to DB > will loose KEYS, only indexes

@app.route("/internet_speed")
def internet_speed_fast():
    global DIVS
    divs, last = read_div_from_db()
    DIVS = {'div' + str(i) : divs[i] for i in [k for k in divs.index] } # rebuilding keys
#    return div
    return render_template('internet_speed.html', #plotly_div1=divs,
                           last_link=last['share'],
                           last_scan=last['datetime'],
                           last_min=last['minutes'],
                           udpate_sec = p.internet_speed.update,
                           **DIVS)


#@app.route("/internet_speed_highchart")
#def internet_speed_hc():
#
#    div1, last = read_div_from_db()
#
#    df = read_data_from_db()[['download','upload','ping','timestamp']].set_index('timestamp')
#    chart = phch_core.serialize(df, render_to='hichart', output_type='json')
##    return div
#    return render_template('internet_speed.html', chart=chart, plotly_div1=div1, last_link=last['share'], last_scan=last['datetime'], last_min=last['minutes'])

#DONE: templates / inject DIV.
#NO: btn 'scan now'
#DONE: link to last scan

#%%
if __name__ == '__main__':
    args = sys.argv[1:]
    if '-speed' in args:
        status = to_db(SpeedTest())
        logger.info(str(status))
    elif '-flask' in args:
        app.run(debug=True, use_debugger = False, use_reloader = False, port = 8082, host = '0.0.0.0')
