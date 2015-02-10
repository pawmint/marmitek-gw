Marmitek Gateway
================

Read data from the Marmitek sensors and transfers it to the server through MQTT, using the ubigate library.

This program has to be set up on the Raspberry Pi Gateway when marmitek sensors are installed in a home.

It can manage:

* MS13 (motion sensor)
* DS90/DS18 (door sensor)

## Config

Marmitek-gw reads config files from two distinct locations:

* $HOME/marmitek-gw/conf.json
* /etc/xdg/marmitek-gw/conf.json

Here is a template `conf.json`:

```
{
  "gateways": [
    {
      "name": "XXX-marmitek",
      "server": "normandie.ubismart.org",
      "port": 1883,
      "username": "normandie",
      "password": "normandie"
    }
  ],
  "houses": [
    {
      "id": "1",
      "name": "My_house",
      "prefix": "A",
      "sensors": [
        "A1",
        "A2",
        "FAF300",
      ]
    }
  ],
  "logging": {
    "file": "info",
    "stdout": "debug"
  }
}
```

## External files

* Event buffer: $HOME/.cache/marmitek-gw/<gateway-name>.json
* Log: $HOME/.cache/marmitek-gw/log/marmitek-gw.log
