# -*- coding: utf-8 -*-
from datetime import datetime
import pytz
import re

from ubigate import logger


def matches(signal, timezone):
    # sample matching input: 11/08 14:42:15 Rx RFSEC Addr: 7E:2D:00 \r
    # Func: Contact_normal_max_tamper_DS12A
    logger.debug('Checking door for signal "%s"' % signal)

    pattern = (r'^(?P<month>\d{2})/(?P<day>\d{2})\s'
               '(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\s'
               'Rx\sRFSEC\sAddr:\s'
               '(?P<sensor1>[0-9A-F]{2}):(?P<sensor2>[0-9A-F]{2}):'
               '(?P<sensor3>[0-9A-F]{2})\s'
               'Func:\sContact_(?P<value>normal|alert)'
               '_(?:max|min)_(?:tamper_)?\w{2}\d+\w$\n*')
    regexp = re.compile(pattern)

    match = regexp.match(signal)

    if not match:
        return None

    logger.info('Door activity detected:')
    tz = pytz.timezone(str(timezone))

    try:
        date = tz.localize(datetime(datetime.now().year,
                                    int(match.group('month')),
                                    int(match.group('day')),
                                    int(match.group('hour')),
                                    int(match.group('minute')),
                                    int(match.group('second'))))
    except ValueError:
        logger.warn('Invalid date: %s-%s-%s %s:%s:%s, event skipped'
                    % (datetime.now().year, match.group('month'),
                        match.group('day'), match.group('hour'),
                        match.group('minute'), match.group('second')))
        return None

    sensor = '%s%s%s' % (match.group('sensor1'),
                         match.group('sensor2'),
                         match.group('sensor3'))

    logger.info("%s: The door sensor %s sent %s"
                % (date.isoformat(),
                    sensor, match.group('value')))

    return {'type': 'event',
            'sensor': sensor,
            'sensorKind': 'door',
            'value': match.group('value'),
            'date': date.isoformat()}
