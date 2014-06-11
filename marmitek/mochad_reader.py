import socket
from ubigate import logger

from marmitek.sensors import motion_signal, door_signal

# TODO Put the config in the config file
MOCHADHOST = "127.0.0.1"
MOCHADPORT = 1099

Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Sock.connect((MOCHADHOST, MOCHADPORT))


def read_from_mochad():
    data = Sock.recv(1024)
    line = repr(data).strip("b'")
    lines = line.split('\\n')
    return lines


def gather_data(signal, timezone):
    signal_types = [motion_signal, door_signal]

    data = None

    for checker in signal_types:
        data = checker.matches(signal, timezone)
        if data is not None:
            break
    return data


def run(timezone):
    while True:
        lines = read_from_mochad()
        for signal in lines[:-1]:
            logger.debug('Signal received: %s' % signal)
            try:
                sensor, data = gather_data(signal, timezone)
                yield sensor, data
            except TypeError:
                pass
