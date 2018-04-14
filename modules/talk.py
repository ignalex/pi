# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 16:19:54 2014
@author: aignatov
v2 - params in class
"""
from __future__ import print_function

import subprocess, urllib, sys, random, os, datetime , tempfile, socket, string
import __main__ as m
#from SHELL import PARAMETERS
from modules.common import  LOGGER, PID, MainException, Dirs
from modules.common import CONFIGURATION as PARAMETERS # fis later

from modules.lock import LockArd as Lock # it has nothing to do with Ard, but still works
from gtts import gTTS

#TODO: disconnect from PA.INI
#TODO: SHELL
#TODO: send speak comand


def Substitutons():
    global p
    if 'p' not in globals(): p = PARAMETERS('PA.INI')
    sub_dict = {'H' : str(datetime.datetime.now().hour),
                'M' : str(datetime.datetime.now().minute),
                'DT' : [t for (n,t) in enumerate(['night','morning','day','evening','night']) if n == int(datetime.datetime.now().hour/5)][0],
                'NAME' : p.INI['NAME']}
    return sub_dict.items()

def PhraseDict():
    global p
    if 'p' not in globals(): p = PARAMETERS('PA.INI')
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

def getSpeech(phrase):
    googleAPIurl = "http://translate.google.com/translate_tts?tl=en_gb&"
    param = {'q': phrase}
    data = urllib.urlencode(param)
    googleAPIurl += data # Append the parameters
    return googleAPIurl

def Speak(text): # This will call mplayer and will play the sound
    global p
    lock = Lock('speak')
    if 'p' not in globals(): p = PARAMETERS('PA.INI')
    for k,v in Substitutons(): text = text.replace('%'+k,v)
    print (text)
    lock.Lock()
    Google_speak(text)
    lock.Unlock()
    print ('---')


def Phrase(about):
    global p
    if 'p' not in globals(): p = PARAMETERS('PA.INI')
    if not p.SPEAK: return
    options = PhraseDict()[about['TYPE']]
    choice = options[int(random.random()*len(options))]
    for k,v in [(a,b) for (a,b) in about.items() if a != 'TYPE']:
        choice = choice.replace('%'+k,v)
    Speak( choice )

class Google_speak(object):
    def __init__(self, text, lang = 'en', store = True):
        self.text, self.lang, self.store = text, lang, store
        #self.Get_GTTS()
        self.check_already_exists()
        self.Speak()
        if not self.store: self.Del()
    def check_already_exists(self):
        self.path_to_speak = os.path.join([i for i in ['/home/pi',os.getcwd()] if os.path.exists(i)][0],'speak')
        if not os.path.exists(self.path_to_speak):
            os.mkdir(self.path_to_speak)
        self.mp3 = os.path.join(self.path_to_speak,name_from_text(self.text) + '.mp3')
        if os.path.exists(self.mp3):
            print ('mp3 exists - OK')
            return True
        else:
            self.Get_GTTS()
            print ('mp3 downloaded - OK')
    def Get_GTTS(self):
        self.tts = gTTS(text=self.text, lang = self.lang)
        #self.mp3 = tempfile.mktemp() + '.mp3'
        print (self.mp3)
        self.tts.save(self.mp3)
    def Speak(self):
        if os.name == 'posix': # Linux
            cmd = "mpg123 " + self.mp3 #cmd = "omxplayer -o local " + self.mp3
        else: # windows
            cmd = 'start ' + self.mp3 + ''
        subprocess.call(cmd.split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print ('ok : ' + self.mp3)
    def Del(self):
        try: os.remove(self.mp3)
        except: pass


def name_from_text(text):
    try:
        return text.translate(str.maketrans('','',""",- !@#$%^&*;:."(')//\\""")).lower()[:255]
    except Exception as e:
        print(str(e))
        return text.translate(None, """,- !@#$%^&*;:."(')//\\""").lower()[:255]

def random_name(x = 10):
    return "".join( [random.choice(string.letters) for i in range(x)] )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "Hello world"
    sys.path.append([i for i in ['/home/pi/PYTHON/GPIO/','/storage/PYTHON/GPIO/','E:\\Dropbox\\PI\\GPIO'] if os.path.exists(i) == True][0])
    #m.talk_params = TALKING_PARAMETERS() # THIS NEEDED IN THE MAIN FILE
    p = PARAMETERS('PA.INI')
    Speak(text)
