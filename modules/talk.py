# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 16:19:54 2014
@author: aignatov
v2 - params in class
"""
from __future__ import print_function
import __main__ as m

try:
    from .common import  LOGGER, Dirs, CONFIGURATION,MainException
    from .lock import LockArd as Lock # it has nothing to do with Ard, but still works
except:
    from common import  LOGGER, Dirs, CONFIGURATION,MainException
    from lock import LockArd as Lock # it has nothing to do with Ard, but still works

import subprocess, sys, random, os, datetime, string, re

from gtts import gTTS
from googletrans import Translator


def Substitutons(): # need also small for RU text > otherwise lines detected as UPPER and not dict element.s
    sub_dict = {'H' : str(datetime.datetime.now().hour), 'h' : str(datetime.datetime.now().hour),
                'M' : str(datetime.datetime.now().minute), 'm' : str(datetime.datetime.now().minute),
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
    options = PhraseDict()[about['TYPE']]
    choice = options[int(random.random()*len(options))]
    for k,v in [(a,b) for (a,b) in about.items() if a != 'TYPE']:
        choice = choice.replace('%'+k,v)
    return Speak( choice )

def Speak(text, store=True):
    #DONE: if p has attr talk > pass it via ssh
    #TODO: avoid errors
    # AttributeError: 'NoneType' object has no attribute 'group'
    if not hasattr(m,'p'):      m.p = CONFIGURATION()
    if not hasattr(m,'logger'): m.logger = LOGGER('TALK', 'INFO')
    for k,v in Substitutons(): text = text.replace('%'+k,v)
    m.logger.debug('SPEAKING ' + text)
    if hasattr(m.p,'talk'): # talk over ssh
        m.logger.debug('passing to ' + str(m.p.talk.ip))
        config = m.p.talk.__dict__
        config['text'] = text
        cmd = "ssh -p {port} -i {ssh} {user}@{ip} nohup python /home/pi/git/pi/modules/talk.py '\"{text}\"'".format(**config) # was with &
        os.system(cmd)
    else: # direct
        lock = Lock('speak'); lock.Lock()
        Google_speak(text, m.p.LANGUAGE, store)
        lock.Unlock()
    m.logger.debug ('---')
    return {'status': True,  'text' : text}


class Google_speak(object):
    "text - in English, land - to speak, store - store mp3 for later of not."
    "if lang != 'en' > translate first (but file stored Eng anyway)"
    def __init__(self, text, lang = 'en', store = True):
        self.text, self.lang, self.store = text, lang, store
        self.mp3 = os.path.join(Dirs()['SPEAK'],name_from_text(self.text) + '.mp3')
        #testing for zero file size
        if os.path.exists(self.mp3):
            if os.path.getsize(self.mp3) == 0:
                m.logger.info('file {} has ZERO size >> deleting'.format(self.mp3))
                self.Del()
        if not os.path.exists(self.mp3): # no file > need to TRANSLATE and DOWNLOAD
            m.logger.debug('no file stored > need to download')
            if self.lang != 'en' and not self.Detect_Russian(): # translate if need RU and text not RU
                self.translate()
            self.Get_GTTS()
        self.Speak()
        if not self.store: self.Del()
    def Detect_Russian(self):
        'detect russian / english by the 1st char'
        return True if ord(self.text[0])>1000 else False
    def translate(self):
        m.logger.debug('translating into ' + self.lang)
        translator = Translator()
        try:
            self.text = translator.translate(self.text, dest=self.lang).text
            m.logger.info(self.text)
        except Exception as e:
            m.logger.error(str(e))
    def Get_GTTS(self):
        m.logger.debug('gTTS >> ' + self.mp3)
        try:
            self.tts = gTTS(text=self.text, lang = self.lang, slow=False)
            self.tts.save(self.mp3)
        except Exception as e:
            m.logger.error(' GTTS failed. error {}'.format(str(e)))
            MainException()
    def Speak(self):
        cmd = ['afplay ' if sys.platform == 'darwin' else 'mpg123 '][0] + self.mp3 # mac vs linux
        subprocess.call(cmd.split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        m.logger.debug ('ok : ' + self.mp3)
    def Del(self):
        m.logger.debug('deleting mp3')
        try: os.remove(self.mp3)
        except:
            m.logger.debug("can't delete mp3")


def name_from_text(text):
    return re.sub(r""",- !@#$%^&*;:."(')//\\""", '', text).replace(' ','').lower()[:250]

def random_name(x = 10):
    try:
        return "".join( [random.choice(string.letters) for i in range(x)] )
    except:
        return "".join( [random.choice(string.ascii_letters) for i in range(x)] )


if __name__ == "__main__":
    logger = LOGGER('TALK', 'INFO')
    p = CONFIGURATION()
    logger.debug ('config read')

    if len(sys.argv) > 1:
        text = ' '.join([ i for i in sys.argv[1:] if i!='-d'])
        if text == '': text = 'Hello world'
    else:
        text = "hello world"
    Speak(text)
