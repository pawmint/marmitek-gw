#!/usr/bin/env python

import logging

from marmitek import mochad_reader

from ubigate import Ubigate
from ubigate import log, logger


def main():
    gate = Ubigate('resources/conf.json')
    log.add_logger_file('data.log', logging.WARN)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting application")
    logger.info('Timezone: %s' % gate.timezone)
    for gateway in gate.config['gateways']:
        logger.info('Server: %s\n'
                    'Port: %s\n'
                    'Password: %s\n'
                    'Gateway: %s\n' % (gateway['server'],
                                       gateway['port'],
                                       gateway['password'],
                                       gateway['name']))

    for data in mochad_reader.run(gate.timezone):
        if data['type'] != 'error':
            try:
                data['house'] = gate.find_house(data['sensor'])
            except KeyError:
                logger.warning("Unknown sensor: %s" % data['sensor'])
            else:
                # Appending house prefix if dealing with door sensor
                if data['sensorKind'] == 'door':
                    prefix = gate.config['houses'][data['house']]['prefix']
                    data['sensor'] = prefix.lower() + data['sensor']

                topic = "/marmitek/sensor/%s" % data['sensor']
                # topic = "/marmitek/sensor/%s/%s" % (data['sensor'],
                #                                     data['type'])
                gate.push(data['house'], topic, data)


if __name__ == "__main__":
    main()
