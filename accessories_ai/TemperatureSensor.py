from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SENSOR
import sys
sys.path.append('/home/pi/git/pi/modules')
from temperature import Temp

class TemperatureSensor(Accessory):

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    @Accessory.run_at_interval(5)
    def run(self):
        self.char_temp.set_value(Temp())