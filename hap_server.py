"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal
import sys
sys.path.append('/home/pi/git/pi/')
# uncommenting this will allow to use GitHub dev branch
#sys.path.append('/home/pi/git/HAP-python/') #TODO: reload from git

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader

# The below package can be found in the HAP-python github repo under accessories/

from accessories_ai.sensors import TemperatureSensor, LightSensor
from accessories_ai.switches import AllSwitches

#logging.basicConfig(level=logging.INFO) #TODO: logging
from common import LOGGER
logger = LOGGER('HAP_server', 'INFO')


def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Bridge')

    temp_sensor = TemperatureSensor(driver, 'temperature')
    light = AllSwitches(driver, 'light')
    heater = AllSwitches(driver, 'heater')
    coffee = AllSwitches(driver, 'coffee')
    lightSenor1 = LightSensor(driver, 'light sensor 1', ip=175)
    lightSenor2 = LightSensor(driver, 'light sensor 2', ip=176)

    bridge.add_accessory(temp_sensor)
    bridge.add_accessory(light)
    bridge.add_accessory(heater)
    bridge.add_accessory(coffee)
    bridge.add_accessory(lightSenor1)
    bridge.add_accessory(lightSenor2)

    return bridge

#
#def get_accessory(driver):
#    """Call this method to get a standalone Accessory."""
#    return TemperatureSensor(driver, 'MyTempSensor')
#
#def get_accessoryLight(driver):
#    """Call this method to get a standalone Accessory."""
#    return Light(driver, 'Light')


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_bridge(driver))
#driver.add_accessory(accessory=get_accessoryLight(driver))

# We want SIGTERM (kill) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()
