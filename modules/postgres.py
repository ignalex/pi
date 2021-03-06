# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 08:30:16 2018

@author: Alexander Ignatov
"""
from __future__ import print_function
from sqlalchemy import create_engine
import pandas as pd
import psycopg2

class PANDAS2POSTGRES(object):
    "READING and WRITING between postgres and pandas"
    def __init__ (self, connect):
        self.connect = connect
        try:
            self.engine = create_engine('postgresql://{USER}:{PASS}@{HOST}:{PORT}/{DB}'.format(**self.connect))
        except:
            self.engine = create_engine('postgresql://{USER}:{PASS}@{SERVER}:{PORT}/{DB}'.format(**self.connect))
        #self.Connection()
    def read(self, sql):
        self.df = pd.read_sql(sql = sql, con = self.engine)
        return self.df
    def write(self, df, name, if_exists = 'append', stamp = None): #, schema = None, ):
        "df is not necessary the one made with 'read'"
        print ('writing ' + str(stamp) + ' ' + str(df.shape[0]) + ' records' )
        self.name = name
#        self.schema =  schema
        df.to_sql( name = name, con = self.engine, if_exists = if_exists)  #schema = schema,
    def Connection(self):
        try:
            self.connection =  "dbname={DB} user={USER} password={PASS} host={HOST} port={PORT}".format(**self.connect)
        except:
            self.connection =  "dbname={DB} user={USER} password={PASS} host={SERVER} port={PORT}".format(**self.connect)
        self.conn = psycopg2.connect(self.connection)
        self.cur = self.conn.cursor()
    def Execute(self,sql):
        self.Connection()
        self.cur.execute(sql)
        self.conn.commit()

def PG_Connect(connect):
    """creates cursor on the database
    inputs: dict {DB, USER, HOST, (PORT - optional - if not provided then 5432), (PASS - optional - if not provided to be taken from .pgpass file)}
    output: (conn,cur)"""

    connection =  ("dbname={DB} user={USER} host={HOST} " + \
                  ['password={PASS} ' if 'PASS' in connect.keys() else ' '][0] + \
                  ['port=5432' if 'PORT' not in connect.keys() else 'port={PORT}'][0]).format(**connect)
    try:
        conn = psycopg2.connect(connection)
        conn.autocommit = True
        cur =  conn.cursor()
        return (conn,cur)
    except:
        return (None,None)