#!/usr/bin/env python

import logging

from marmitek import mochad_reader

from ubigate import Ubigate
from ubigate import log, logger


def main():
    gate = Ubigate('resources/conf.ini')
    log.add_logger_file('data.log', logging.WARN)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting application")
    logger.info('Server: %s\n'
                'Port: %s\n'
                'Password: %s\n'
                'House: %s\n'
                'Gateway: %s\n'
                'Timezone: %s' % (gate.config.server,
                                  gate.config.port,
                                  gate.config.password,
                                  gate.config.house,
                                  gate.config.gateway,
                                  gate.timezone))

    for meta_data, data in mochad_reader.run(gate.timezone):
        if meta_data['type'] == 'error':
            break
        topic = "/marmitek/sensor/%s/%s" % (meta_data['sensor'], meta_data['type'])
        data['house'] = gate.config.house
        gate.push(topic, data)


if __name__ == "__main__":
    main()
