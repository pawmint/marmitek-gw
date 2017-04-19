from ubigate.plugin_categories.sensor_plugin import SensorPlugin
import domoticz_to_marmitek
from ubigate.log import logger
class Domoticz_as_Marmitek(SensorPlugin):
    """Adaptor Sensor Plugin for Z-Wave sensors connected to Domoticz.
    Messages are in Marmitek format so that UbiSmart platform does not need to be adapted.
    """
    name = "Domoticz_as_Marmitek"
    topic = "marmitek"
    myMAC = open('/sys/class/net/eth0/address').read()
    def run(self):
        logger.info("Starting Domoticz as Marmitek Gateway")
        domoticz_to_marmitek.run(self)
    def get_details_deprecated(self, sensor):
        try:
            house = [house['id']
                    for house in self.gate.config['houses']
                    for s in house['sensors']
                    if s['id'] == sensor][0]
            details = [s for h in self.gate.config['houses'] if h['id'] == house for s in h['sensors'] if s['id'] == sensor][0]
            logger.info("details: " + str(details) + "   house: " + str(house))
            return {'house': house, 'binding': details['binding'], 'bindingType': details['bindingType']}
        except Exception as e:
            logger.error("D2M get_details_deprecated" + str(e))
            logger.debug("Unknown sensor \"%s\"" % sensor)
            return {'house': None, 'binding': None, 'bindingType': None}
