# DS18B20
Use a Raspberry Pi Pico W to read a DS18B20 Temperature sensor and publish data using MQTT

The basic structure for the MicroPython code in this git is copied from https://github.com/HenrikSolver/picowhanport.

For general notes on MicroPython, refer to https://github.com/mats-bergstrom/halix/tree/main/BluePi.

You need to edit `config.py` to correcpond to the SSID and PSK of your WLAN.  `MQTTHost` need to be updated to the IP number of your broker to use.

Files:
| File | Description |
| --- | --- |
| config.py | WLAN and MQTT configuration. |
| boot.py | Just direct execution to main.py. |
| main.py | Main code |
| DS18B20SBS-B.stl | Bottom casing for Pico and PCB |
| DS18B20SBS-top-B.stl | Top casing for Pico and PCB |

Note that the code (`main.py`) is made to read two independent
one-wire interfaces fed using a 3v3 regulator.  If you only need one,
you need to edit the code.  Depending on your number of sensors, the
Pico's build-in 3v3 might just be able to handle a sensor or two,
depending on the brand of sensor and cable lengths.

The two sensors are connected to pins 16 and 17, respectively.

The Pico will publish MQTT topics as `hus/<ID>/0/T` and
`hus/<ID>/1/T`, for the sensor 0 connected to pin 16, and sensor 1
connected to pin 17. `<ID>` is an id number determined at boot up by
reading pins 6-9 pulled to ground (no pin pulled to ground = '0x0',
all pins pulled to gound = '0xf').

The frequency the sensors are read is set by reading pins 10-11 pulled
to ground at boot time to give a number 0 to 3 with the read
frequencies 10s, 5min, 15min 30min.



