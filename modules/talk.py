# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 16:19:54 2014
@author: aignatov
v2 - params in class
"""
from __future__ import print_function
import __main__ as m

import subprocess, sys, random, os, datetime, string, re
from common import  LOGGER, Dirs, CONFIGURATION

from lock import LockArd as Lock # it has nothing to do with Ard, but still works
from gtts import gTTS
from googletrans import Translator


def Substitutons():
    sub_dict = {'H' : str(datetime.datetime.now().hour),
                'M' : str(datetime.datetime.now().minute),
                'DT' : [t for (n,t) in enumerate(['night','morning','day','evening','night']) if n == int(datetime.datetime.now().hour/5)][0],
                'NAME' : m.p.INI['NAME']}
    return sub_dict.items()

def PhraseDict():
    try:
        INI_file = open(os.path.join(Dirs()['DATA'],'phrases.ini'),'r').read().splitlines()
    except:
        return False

    INI_file = [i for i in INI_file if len(i) != 0] # empty strings
    INI_file = [i for i in INI_file if i[0] != '#']

    param, GROUP = {}, ''

    for p_item in INI_file:
        if p_item.isupper():
            GROUP = p_item.replace(' ','')
            param[GROUP] = []
        else:
            param[GROUP].append(p_item)
    return param

def Phrase(about):
#    if 'p' not in globals(): p = PARAMETERS('PA.INI')
    options = PhraseDict()[about['TYPE']]
    choice = options[int(random.random()*len(options))]
    for k,v in [(a,b) for (a,b) in about.items() if a != 'TYPE']:
        choice = choice.replace('%'+k,v)
    Speak( choice )

def Speak(text):
    for k,v in Substitutons(): text = text.replace('%'+k,v)
    m.logger.debug(text)
    lock = Lock('speak'); lock.Lock()
    Google_speak(text, m.p.LANGUAGE)
    lock.Unlock()
    m.logger.debug ('---')


class Google_speak(object):
    def __init__(self, text, lang = 'en', store = False):
        self.text, self.lang, self.store = text, lang, store
        if self.lang != 'en':
            self.translate()
        self.get_mp3()
        self.Speak()
        if not self.store: self.Del()
    def get_mp3(self):
        self.path_to_speak = os.path.join([i for i in ['/home/pi','/Users/s84004/temp', os.getcwd()] if os.path.exists(i)][0],'speak')
        if not os.path.exists(self.path_to_speak):
            os.mkdir(self.path_to_speak)
#        try:
#            self.mp3 = os.path.join(self.path_to_speak,name_from_text(self.text) + '.mp3')
#        except:
        self.mp3 = os.path.join(self.path_to_speak,random_name(20) + '.mp3') #FIXME: bad patch

        if os.path.exists(self.mp3):
            m.logger.debug ('mp3 exists - OK')
            return True
        else:
            self.Get_GTTS()
            m.logger.debug ('mp3 downloaded - OK')
    def Get_GTTS(self):
        self.tts = gTTS(text=self.text, lang = self.lang, slow=False)
        #self.mp3 = tempfile.mktemp() + '.mp3'
        m.logger.debug (self.mp3)
        self.tts.save(self.mp3)

    def translate(self):
        translator = Translator()
        try:
            self.text = translator.translate(self.text, dest=self.lang).text
            m.logger.info(self.text)
        except Exception as e:
            m.logger.error(str(e))

    def Speak(self):
        cmd = ['afplay ' if sys.platform == 'darwin' else 'mpg123 '][0] + self.mp3 # mac vs linux
        subprocess.call(cmd.split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        m.logger.debug ('ok : ' + self.mp3)

    def Del(self):
        try: os.remove(self.mp3)
        except: pass


def name_from_text(text):
    return re.sub(r""",- !@#$%^&*;:."(')//\\""", '', text).lower()[:250]

def random_name(x = 10):
    try:
        return "".join( [random.choice(string.letters) for i in range(x)] )
    except:
        return "".join( [random.choice(string.ascii_letters) for i in range(x)] )


if __name__ == "__main__":

    logger = LOGGER('PA', 'INFO')
    p = CONFIGURATION()

    if len(sys.argv) > 1:
        text = ' '.join([ i for i in sys.argv[1:] if i!='-d'])
        if text == '': text = 'Hello world'
    else:
        text = "Hello world"
    Speak(text)
