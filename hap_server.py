"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import signal
import sys
sys.path.append('/home/pi/git/pi/')

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver
#import pyhap.loader as loader

# The below package can be found in the HAP-python github repo under accessories/

from accessories_ai.sensors import TemperatureSensor, LightSensor#, InternetSpeed
from accessories_ai.switches import AllSwitches, EspStatusCollector, ProgramableSwitch
from accessories_ai.windows import WindowCovering
from accessories_ai.computers import SYSTEM

from common import LOGGER
logger = LOGGER('HAP_server', 'DEBUG')

from talk import Speak
Speak('starting HAP server')

st = EspStatusCollector() # starting threaded status collector, must have name 'st'

def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Bridge')

    temp_sensor = TemperatureSensor(driver, 'temperature')
    light = AllSwitches(driver, 'light')
    light_ambient = AllSwitches(driver, '14')
    heater = AllSwitches(driver, 'heater')
    coffee = AllSwitches(driver, 'coffee')
    lightSenor1 = LightSensor(driver, 'light sensor 1', ip=175)
    lightSenor2 = LightSensor(driver, 'light sensor 2', ip=176)
    window = WindowCovering(driver, 'window', ip=175, calibrate=True, speak=True, minStep=10)
    beep = AllSwitches(driver, 'beep')
    program1 = ProgramableSwitch(driver,'program 1')
    watering = AllSwitches(driver, 'watering')
    hippo = SYSTEM(driver, 'hippopotamus')
#    raid = SYSTEM(driver, 'raid')

   # internet_speed = InternetSpeed(driver,'internet speed', task='download') #!!!: will wait till right type of sensor

    bridge.add_accessory(temp_sensor)
    bridge.add_accessory(light)
    bridge.add_accessory(heater)
    bridge.add_accessory(coffee)
    bridge.add_accessory(lightSenor1)
    bridge.add_accessory(lightSenor2)
    bridge.add_accessory(window)
    bridge.add_accessory(beep)
    bridge.add_accessory(program1)
    bridge.add_accessory(watering)
    bridge.add_accessory(light_ambient)
    bridge.add_accessory(hippo)
#    bridge.add_accessory(raid)

  #  bridge.add_accessory(internet_speed)

    return bridge

driver = AccessoryDriver(port=51826)
driver.add_accessory(accessory=get_bridge(driver))
signal.signal(signal.SIGTERM, driver.signal_handler)
driver.start()
Speak('stopping HAP server')
st.Stop()
