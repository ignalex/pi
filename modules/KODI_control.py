# -*- coding: utf-8 -*-
"""
control KODI music via JSON http interface

Created on Fri Apr 25 12:42:08 2014
@author: ignalex
"""
import urllib2

#TODO: address hardcoding
#TODO: PY3 

def KODI_JSON(com='play_current', kodi = 'http://192.168.1.153:8080'):
    commands = {'play_current'    : "{}/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22id%22:1,%22method%22:%22Player.Open%22,%22params%22:{%22item%22:{%22playlistid%22:0},%22options%22:{%22repeat%22:%22all%22}}}",
                'pause'           : "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Player.PlayPause%22%2C%20%22params%22:%20%7B%20%22playerid%22:%200%20%7D%2C%20%22id%22:%201%7D",
                'resume'          : "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Player.PlayPause%22%2C%20%22params%22:%20%7B%20%22playerid%22:%200%20%7D%2C%20%22id%22:%201%7D",                
                'playpause'       : "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Player.PlayPause%22%2C%20%22params%22:%20%7B%20%22playerid%22:%200%20%7D%2C%20%22id%22:%201%7D",                                
                'what_is_playing' : "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Player.GetActivePlayers%22%2C%20%22id%22:%201%7D",
                'next'            : "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Player.GoTo%22%2C%20%22params%22:%20%7B%20%22playerid%22:%200%2C%20%22to%22:%20%22next%22%20%7D%2C%20%22id%22:%201%7D",                 
                'volume'          : "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Application.GetProperties%22%2C%20%22params%22:%20%7B%22properties%22:%20%5B%22volume%22%5D%7D%2C%20%22id%22:%201%7D", 
                'up'              : "{}/jsonrpc?request=%7B%20%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Application.SetVolume%22%2C%20%22params%22:%20%7B%20%22volume%22:%20%22increment%22%20%7D%2C%20%22id%22:%201%20%7D",#"{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Application.SetVolume%22%2C%20%22params%22:%20%7B%22volume%22:%20100%7D%2C%20%22id%22:%201%7D",
                'down'            : "{}/jsonrpc?request=%7B%20%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Application.SetVolume%22%2C%20%22params%22:%20%7B%20%22volume%22:%20%22decrement%22%20%7D%2C%20%22id%22:%201%20%7D", #"{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Application.SetVolume%22%2C%20%22params%22:%20%7B%22volume%22:%2050%7D%2C%20%22id%22:%201%7D"
                'current'         : "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Player.GetItem%22%2C%20%22params%22:%20%7B%20%22properties%22:%20%5B%22title%22%2C%20%22album%22%2C%20%22artist%22%2C%20%22duration%22%2C%20%22thumbnail%22%2C%20%22file%22%2C%20%22fanart%22%2C%20%22streamdetails%22%5D%2C%20%22playerid%22:%200%20%7D%2C%20%22id%22:%20%22AudioGetItem%22%7D",
                'getPlaylists'    : "{}/jsonrpc?request=%7B%22jsonrpc%22:%222.0%22%2C%22id%22:1%2C%22method%22:%22Playlist.GetPlaylists%22%2C%22params%22:%5B%5D%7D", 
                'getItems'        : "{}/jsonrpc?request=%7B%22jsonrpc%22:%222.0%22%2C%22id%22:1%2C%22method%22:%22Playlist.GetItems%22%2C%22params%22:%7B%22playlistid%22:0%7D%7D"
                }
    command = commands[com].formant(kodi) #with HTTP address
    if com.startswith('vol') and com != 'volume': 
        new = com.replace('vol','').replace('_','')
        commands['vol'] = "{}/jsonrpc?request=%7B%22jsonrpc%22:%20%222.0%22%2C%20%22method%22:%20%22Application.SetVolume%22%2C%20%22params%22:%20%7B%22volume%22:%20"+new+"%7D%2C%20%22id%22:%201%7D".formant(kodi)
        com = 'vol'
        
    replies = {'{"id":1,"jsonrpc":"2.0","result":[{"playerid":0,"type":"audio"}]}' : 'audio', 
               '{"id":1,"jsonrpc":"2.0","result":[]}' : 'nothing', 
               '{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"type":"video"}]}' : 'video'
               }

    res = urllib2.urlopen(command).read()
    if com =='pause' and res == '{"id":1,"jsonrpc":"2.0","result":{"speed":1}}':  res = urllib2.urlopen(command).read() 
    if com =='resume' and res == '{"id":1,"jsonrpc":"2.0","result":{"speed":0}}':  res = urllib2.urlopen(command).read() 

    if com =='what_is_playing': 
        try: 
            res = replies[res]
        except: 
            pass
    return res

if __name__ == "__main__":
    KODI_JSON()