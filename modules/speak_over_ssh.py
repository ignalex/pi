# -*- coding: utf-8 -*-
"""
sending speaking command to another PI (octopus)
uses SSH to connect to another device, so teh SSH key has to be configured beforehand 
** ssh key has to be chmod 600 

Created on Sat Aug 26 17:32:42 2017
@author: Alexander Ignatov
"""
import os, random, datetime
from common import CONFIGURATION, Dirs

def Speak(text, device = 'octopus' ): 
    'simple speaking function integration to use gTTS on another PI' 
    global p
    if 'p' not in globals(): p = CONFIGURATION()  
    for k,v in Substitutons(): text = text.replace('%'+k,v)
    keys ={'octopus' : '192.168.1.154:2227', 'hornet' : '192.168.1.153:2226'}
    os.system("ssh -p {} -i /home/pi/.ssh/{} pi@{} nohup sudo python /home/pi/PYTHON/GPIO/modules/talk.py '\"".\
        format(keys[device].split(':')[1], 
               device, 
               keys[device].split(':')[0]) +text+"\"'")
    return 

#TODO: replace this with GROUPED params 
def Phrase(about): 
    "Phrase({'TYPE' : 'type_from_phrases'})"
    global p 
    if 'p' not in globals(): p = CONFIGURATION()
    if hasattr(p, 'SPEAK'): # if not in the config - skip checks 
        if not p.SPEAK: return 

    def PhraseDict():
        try: 
            INI_file = open(os.path.join(Dirs()['DATA'],'phrases.ini'),'r').read().splitlines() #TODO: fix path
        except: 
            print ("can't open phrases ini file")
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
    try: 
        options = PhraseDict()[about['TYPE']]
        choice = options[int(random.random()*len(options))]
        for k,v in [(a,b) for (a,b) in about.items() if a != 'TYPE']: 
            choice = choice.replace('%'+k,v)
        Speak( choice ) 
    except: 
        print ('cant find phrase')
        return 

def Substitutons():
    global p 
    if 'p' not in globals(): p = CONFIGURATION()
    return {'H' : str(datetime.datetime.now().hour), 
            'M' : str(datetime.datetime.now().minute), 
            'DT' : [t for (n,t) in enumerate(['night','morning','day','evening','night']) if n == int(datetime.datetime.now().hour/5)][0], 
            'NAME' : p.NAME}.items()

if __name__ == '__main__': 
  Speak('Hello world')