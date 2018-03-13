# kodi
# sudo apt-get install kodi



# gps daemon
    # https://learn.adafruit.com/adafruit-ultimate-gps-on-the-raspberry-pi?view=all
    # sudo apt-get install gpsd gpsd-clients python-gps
    # sudo pip3 install gps3

    # pointing socket to USB
    # sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock

    # if needed to be stopped and disabled
    # sudo systemctl stop gpsd.socket
    # sudo systemctl disable gpsd.socket

    ## enable
    # sudo systemctl enable gpsd.socket
    # sudo systemctl start gpsd.socket

    #to kill and reenable GPS
    #sudo killall gpsd
    #sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
