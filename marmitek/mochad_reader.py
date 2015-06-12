# -*- coding: utf-8 -*-
import socket
import select
import time

from ubigate import logger

from marmitek.sensors import motion_signal, door_signal


def _init():
    # TODO Put the config in the config file
    MOCHADHOST = "127.0.0.1"
    MOCHADPORT = 1099

    while True:
        try:
            Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            Sock.connect((MOCHADHOST, MOCHADPORT))
            Sock.settimeout(10)
            logger.debug("Successfully connected to Mochad")
            return Sock
        except socket.error as e:
            Sock.close()
            logger.error("Unable to listen from Mochad : %s" % e)
            time.sleep(5)


def read_from_mochad():
    while True:
        Sock = _init()
        try:
            data = Sock.recv(1024)
            line = repr(data).strip("b'")
            lines = line.split('\\n')
            yield lines
        except socket.timeout:
            logger.warning("Will try to reconnect to mochad")
        finally:
            Sock.shutdown(2)
            Sock.close()


def gather_data(signal, timezone):
    signal_types = [motion_signal, door_signal]

    for checker in signal_types:
        data = checker.matches(signal, timezone)
        if data is not None:
            return data
    return None


def run(timezone):
    lastDoorEvents = {}
    for lines in read_from_mochad():
        for signal in lines[:-1]:
            logger.debug('Signal received: %s' % signal)
            data = gather_data(signal, timezone)
            if data is None:
                continue
            sensor = data['sensor']
            if not(data['sensorKind'] == 'door'
                   and lastDoorEvents.get(sensor, "") == data['value']):
                if data['sensorKind'] == 'door':
                    lastDoorEvents[sensor] = data['value']
                yield data
