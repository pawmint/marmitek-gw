#!/usr/bin/env python

import sys

from ubiGATE.ubigate.utils.logger import logger
#from ubiGATE.ubigate.communication.http_pusher import DataPusher
from ubiGATE.ubigate.communication import mqtt_pusher
#from ubiGATE.ubigate.communication.http_thread import HttpThread
from ubiGATE.ubigate.config import conf

from sensors import motion_signal, door_signal


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


logger.info("Starting application")
server, house, username, password = conf.get_options()
#data_pusher = DataPusher(server, house, username, password)
logger.info('Server: %s\n'
            'House: %s\n'
            'Username: %s' % (server, house, username))

#httpThread = HttpThread(data_pusher)
#httpThread.start()

mqtt = mqtt_pusher.broker_connection("marmitek_sensors", "127.0.0.1")

stop = 0
topic = "my/topic"

while stop == 0:

    signal = get_signal()
    logger.debug('Signal received: %s' % signal)
    data = gather_data(signal)
    if data is not None:
#        data_pusher.push_data(data)
#        data_pusher.send()
        mqtt_pusher.push_data(data, house)
        stop = mqtt_pusher.send(mqtt, topic)

mqtt_pusher.disconnection(mqtt)


