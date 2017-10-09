# pi
raspberry pi modules for home automation

[to do in progress... ](https://github.com/ignalex/pi/blob/master/TODO.md)

##  projects
- **MS** > 'manage services' > to turn things ON/OFF based on the conditions
- **PA** > 'personal assistant' > using iCalendar and other mods to trigger functions
- **WATERING** > using 2 (or more / or less) independent systems, open / close valves and trigger motor to start watetring plants
    * using BOM forecast for temperature / rain to tailor the amount of water
- **HEATER** control > keeping temperature inside within defined range
    * used temperature sensor (GPIO), esp/rf433 api to wireless power outlet to remote control ON/OFF

## functionality
- **relay** > control relay via GPIO
- **watering** > water flowers [set for 2 systems] based on forecasted temperature (BOM) and previous day rain (BOM)
- **weather** >
  * current temperature inside
  * current and forecast for specified point
- **LCD** > deliver info on Ardiuino's LCD screen
    * weather now and forecast, temperature inside, next ferry, time.
- **talk** > speaking using gTTs API
    * incl sending speaking command to another PI
- **ferry** timetable > next ferry is in ... min
- **ping iPhone bluetooth** > to know if you are home or not and turn ON/OFF things
- **wol** > Wake On LAN > send magic packet to another PC to wake up
- **sunrise/sunset** > times ** to be changed to pvlib integration??
- **play** music control (via KODI http API)
- **ESP integration** > for using wifi remoted [ESP](https://github.com/ignalex/esp)
- **send email** > smtp email integration
- **movement sensor** > integration to MS.
    * depends on time of the day, __on movement__ > turn on/off lights, blinds up/down, **start boiling cooffee :)**
- **git_hooks** > GIT CI > on git hook make 'git pull' and confirm (email + speaking)
- **light** control  (via http API talking to ESP)
- **lirc_mod** (IR reciever)
  * integration to play music
  * light ON/OFF from using IR remote
  * blinds ON/OF (using http API to ESP)
  * more
- **dynamic IP** > if changes - send email.

- **internet speed** > ping and speed test every ... min and having results on web     >> __to be migrated__
- **location tracking** > track iPhone location and measure distance to home to ON/OFF things  >> __to be migrated__
- **ISS** > track ISS (International Space Station) location and distance to home and speak when close  >> __to be migrated__
- **ant** > communicate to another PI using SSH >> __to be migrated__
- **camera** > using camera vid / pic (used in ALARM for email pic if there is moovement and I am not at home)  >> __to be migrated__
*** __more to come ;)__

## installation and deployment
TBD

## dependencies python mods
TBD

![image](https://user-images.githubusercontent.com/7232721/29808545-ebaa712e-8cdb-11e7-9bd1-6174e16728f1.png)