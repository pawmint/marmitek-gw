from ubigate.plugin_categories.sensor_plugin import SensorPlugin

import mochad_reader

from ubigate.log import logger


class Marmitek(SensorPlugin):
    name = "Marmitek"
    topic = "marmitek"

    def run(self):
        logger.info("Starting Marmitek-Gateway")

        for data in mochad_reader.run():
	    self.push_event(data['sensor'], data['value'], data['date'], data['id'], data['type'], data['observedProperty'], data['procedure'], data['featureOfInterest'], data['uom'])
