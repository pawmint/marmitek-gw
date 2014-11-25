#!/usr/bin/env python

from marmitek import mochad_reader

from ubigate import Ubigate, logger


def main():
    gate = Ubigate('marmitek-gw',
                   default_file='resources/conf.json.default')

    logger.info("Starting application")
    logger.debug('Timezone: %s' % gate.timezone)

    for data in mochad_reader.run(gate.timezone):
        if data['type'] != 'error':
            try:
                data['house'] = gate.find_house(data['sensor'])
            except KeyError:
                logger.warning("Unknown sensor: %s" % data['sensor'])
            else:
                # Appending house prefix if dealing with door sensor
                if data['sensorKind'] == 'door':
                    for house in gate.config['houses']:
                        if house['id'] == data['house']:
                            prefix = house['prefix']
                            break
                    else:
                        prefix = ''
                    data['sensor'] = prefix.lower() + data['sensor']

                topic = "/marmitek/sensor/%s" % data['sensor']
                gate.push(data['house'], topic, data)


if __name__ == "__main__":
    main()
