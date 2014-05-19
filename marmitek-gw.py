#!/usr/bin/env python

import sys
import logging

from ubigate import Ubigate
from ubigate import log, logger
from marmitek.sensors import motion_signal, door_signal


def get_signal():
    return sys.stdin.readline()


def gather_data(signal):
    signal_types = [motion_signal, door_signal]

    data = None

    for checker in signal_types:
        data = checker.matches(signal)
        if data is not None:
            break
    return data


def main():
    gate = Ubigate('resources/conf.ini')
    log.add_logger_file('data.log', logging.WARN)
    logger.setLevel(logging.DEBUG)

    logger.info("Starting application")
    logger.info('Server: %s\n'
                'Port: %s\n'
                'House: %s\n'
                'Username: %s' % (gate.config.server,
                                  gate.config.port,
                                  gate.config.house,
                                  gate.config.username))

    while True:
        signal = get_signal()
        logger.debug('Signal received: %s' % signal)
        try:
            sensor, data = gather_data(signal)
            topic = "/marmitek/%s" % sensor

            gate.push(topic, data)
        except TypeError:
            pass


if __name__ == "__main__":
    main()
