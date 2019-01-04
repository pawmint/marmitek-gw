# -*- coding: utf-8 -*-
#from ubigate import credentials, gateway_config
#from ubigate.buffer import MessagesBuffer
#from ubigate.keepaliveNotifier import KeepaliveNotifier

# MQTT broker
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time

# Needed?
from datetime import datetime
try:
    import simplejson as json
except ImportError:
    import json
from ubigate.buffer import MessagesBuffer
from ubigate.log import logger

# Get time
import pytz
from tzlocal import get_localzone

def run(plugin):
    # TODO Move config in the config file
    DOMOTICZHOST = "127.0.0.1"
    DOMOTICZPORT = 1883
    QOS = 1  # Quality of service
    KEEPALIVE = 60  # The client stays connected for []s without handshake
    RETAIN = False

    while True:
        try:
            client = mqtt.Client()
            client.connect(DOMOTICZHOST, DOMOTICZPORT, KEEPALIVE)
            client.plugin = plugin # refer to UbiGate object

            client.on_connect = on_connect
            client.on_message = on_message

            client.loop_forever()
            logger.info("MQTT client for Domoticz sucessfully initialised")
        except Exception as e:
            logger.error('MQTT client for Domoticz Error: ' + str(e))
            # Wait some time before re-trying
            time.sleep(5)
    else:
        print('Gateway not linked to UbiSmart')
 
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code " + str(rc))
    client.subscribe("domoticz/out")

def on_message(client, userdata, msg):
    def push_signal(sensor, values, date):#, id, type, observedProperty, procedure, featureOfInterest, uom):
        """Push a sensor event to Ubismart through MQTT.
        If the sensor is known, we send it to house/<ID>/<plugin>/sensor/<ID>.
        If the sensor is unknown, we send it to gateway/<ID>/sensor/register.
        If the sensor known and blacklisted, we skip it.
        """
        logger.info("Sending event '%s' at time '%s' for sensor '%s'" %
                    (value, date, sensor))
        try:
            # List comprehensions are cool!
            house = [house['id']
                     for house in client.plugin.gate.config['houses']
                     for s in house['sensors']
                     if s['id'] == sensor][0]
        except IndexError:
            # If the sensor isn't in the config
            if('blacklist' not in client.plugin.gate.config or
               sensor not in client.plugin.gate.config['blacklist']):
                logger.info("Unknown sensor, notifying to Ubismart")
                # If it's not blacklisted
                topic = ("gateway/%s/sensor/register"
                         % client.plugin.gate.credentials['id'])
                data = {"sensor": sensor,
                        "id": sensor,
                        "state": "signal",
                        "date": date,
                        "format": "temphum"}
                client.plugin.gate.mqtt_buffer.lock.acquire()
                mid = client.plugin.gate.push(topic, data, to_buffer=True)
                client.plugin.gate.mqtt_buffer.add(mid, topic, data)
                client.plugin.gate.mqtt_buffer.lock.release()
            else:
                logger.info('This sensor is blacklisted, message skipped')
        except KeyError:
            logger.error("Can't send sensor event, missing config")
        else:
            signal = {}
            signal['sensor'] = sensor
            signal['house'] = house
            signal['values'] = values
            signal['date'] = date
            signal['format'] = 'temphum'
            topic = "signal"
            # By using locks, we ensure we won't ever have I/O conflict
            client.plugin.gate.mqtt_buffer.lock.acquire()
            mid = client.plugin.gate.push(topic, signal, to_buffer=True)
            client.plugin.gate.mqtt_buffer.add(mid, topic, signal)
            client.plugin.gate.mqtt_buffer.lock.release()


    value = None
    data=msg.payload.decode()
    data= json.loads(data)
    tz = pytz.timezone(str(get_localzone()))
    date = tz.localize(datetime.now()).isoformat()
    try: 
        if u'Temp + Humidity' in data['dtype']:
            logger.info("Z-wave received temp/hum data:" + str(data))
            sensor = data['name']
            values = {'temperature': data['svalue1'], 'humidity': data['svalue2']}
            push_signal(sensor, values, date)

        if any(['Contact' in data['name'], 'Motion' in data['name']]):
            logger.info("Z-wave received some data:" + str(data))
            sensor = data['name']
            details = client.plugin.get_details_deprecated(sensor)
            if 'Contact' in data['name']:
                if data['nvalue'] == 1:
                    value = "alert"
                else:
                    value = "normal"
            if 'Motion' in data['name']:
                if data['nvalue'] == 1:
                    value = "on"
                else:
                    value = "off"
            myMAC = open('/sys/class/net/eth0/address').read().rstrip()
            result = {}
            result['type']= "TruthObservation"
            result['observedProperty']= data['switchType'] # Contact or Motion
            result['procedure']= "Zwave_%s_%s_%s" % (sensor, details['binding'], details['bindingType'])
            result['featureOfInterest']= details['house']
            result['uom'] = '' # unit of measurement
            #result['id']= "Raspberry_Pi/%s/Zwave_%s_Room" % (client.ubigate.credentials['id'],sensor)
            result['id'] = '/'.join (['Raspberry_Pi', myMAC, result['procedure'], date])

            client.plugin.push_event(sensor, value, date, result['id'], result['type'], result['observedProperty'], result['procedure'], result['featureOfInterest'], result['uom'])

    except KeyError:
        pass
    except Exception as e:
        try: details
        except NameError: details = str(values)
        try: sensor
        except NameError: sensor = "unknown sensor"
        logger.info("D2M: Exception: " + str(e) + "   " + str(details) + "  " + sensor) 
   


# No more used -- this is done in sensor_plugin.py
def push_eventx(client, msg, sensor, value):
    """Push a sensor event to Ubismart through MQTT.
    If the sensor is known, we send it to house/<ID>/<plugin>/sensor/<ID>.
    If the sensor is unknown, we send it to gateway/<ID>/sensor/register.
    If the sensor known and blacklisted, we skip it.
    """
    tz = pytz.timezone(str(get_localzone()))
    date = tz.localize(datetime.now()).isoformat()
    logger.debug("BROKER: pushing an event at ", date)
    try:
        # List comprehensions are cool!
        house = [house['id']
            for house in client.ubigate.config['houses']
                #for house in config['houses'] # if not in use, remove the global variable
                for s in house['sensors']
                if s['id'] == sensor][0]
    except IndexError:
        logger.debug("Sensor %s not found in the config %s" % (sensor, client.ubigate.config['houses']))
        # If the sensor isn't in the config
        if('blacklist' not in config or
                sensor not in config['blacklist']):
            logger.info("Unknown sensor, notifying to Ubismart")
            # If it's not blacklisted
            topic = ("gateway/%s/sensor/register"
                     % credentials['id'])
            data = {"id": sensor,
                    "state": value,
                    "date": date}
            client.ubigate.push(topic, json.dumps(data))
        else:
            logger.info('This sensor is blacklisted, message skipped')
    except KeyError:
        logger.error("Can't send sensor event, missing config")
    else:
        measurement['id']= "Raspberry_Pi/%s/Zwave_%s_Room" % (client.ubigate.credentials['id'],sensor)
        measurement['type']= "TruthObservation"
        measurement['phenomenonTime']= {'instant': date}
        #measurement['observedProperty']= {'href': observedProperty}
        measurement['procedure']= "Zwave_%s_%s" % (sensor, house)
        measurement['featureOfInterest']= {'href': house}
        measurement['resultTime']= date
        measurement['result']= {'value': value}#, 'uom': uom}

        topic = "house/%s/marmitek/sensor/%s" % (house, sensor)
        client.ubigate.push(topic, measurement)


def main(plugin): 
    run(plugin)

if __name__ == '__main__':
    main()

