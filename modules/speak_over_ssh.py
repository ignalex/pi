# -*- coding: utf-8 -*-
"""
sending speaking command to another PI (octopus)
uses SSH to connect to another device, so teh SSH key has to be configured beforehand 
** ssh key has to be chmod 600 

Created on Sat Aug 26 17:32:42 2017
@author: Alexander Ignatov
"""
import os 

def Speak(text, device = 'octopus' ): 
  'simple speaking function integration to use gTTS on another PI' 
  
  keys ={'octopus' : '192.168.1.154:2227', 'hornet' : '192.168.1.153:2226'}
  os.system("ssh -p {} -i /home/pi/.ssh/{} pi@{} nohup sudo python /home/pi/PYTHON/GPIO/modules/talk.py '\"".\
            format(keys[device].split(':')[1], 
                   device, 
                   keys[device].split(':')[0]) +text+"\"'")
  return 

if __name__ == '__main__': 
  Speak('Hello world')