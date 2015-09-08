from ubigate.plugin_categories.sensor_plugin import SensorPlugin

from marmitek import mochad_reader


class Marmitek(SensorPlugin):
    name = "Marmitek"
    topic = "marmitek"

    def run(self):
        self.logger.info("Starting Marmitek-Gateway")

        for data in mochad_reader.run(self.gate.timezone):
            self.push_event(data['sensor'], data['value'], data['date'])
