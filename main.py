# using 2 pins to read the 2 sensors as it is more stable.

import machine, onewire, ds18x20, time, gc
from machine import Pin
from umqtt.simple import MQTTClient
from time import sleep
import network
import config


Pin0 = 16
Pin1 = 17
IDPins = [6,7,8,9]
DelayPins = [10,11]

MQTTTopic0 = 'hus/T%02x/0/T'
MQTTTopic1 = 'hus/T%02x/1/T'



# Get GPIO input from list of pins, note inverted, strapped to GND gives 1
def get_pins( A ):
   rval = 0;
   v = 1;
   for i in A:
      pID = i
      p = Pin( pID, Pin.IN, Pin.PULL_UP )
      pval = p.value()
      p.init( p.IN, p.PULL_DOWN )       # DONE: Pull down to save power!
      if pval == 0:
         rval += v
      v *= 2
   return rval

# Get ID number from pins
def get_ID():
   return get_pins(IDPins)

# Get delay in s from pins
def get_Delay():
   i = get_pins(DelayPins)
   A = [ 
         10,                    # 0: 10s
       5*60,                    # 1:  5min
      15*60,                    # 2: 15min
      30*60                     # 3: 30min
   ]
   if i>3:
      i=3
   return A[i]



# Figure out what ID to use in the topics. pins 6-9 strapped to GND
id = get_ID()
print("ID = %d" % id)

topicT0 = MQTTTopic0 % id
topicT1 = MQTTTopic1 % id
print("topics = " + topicT0 + "," + topicT1)


# Set the hostname
hname = "rPIp_DF12B20_%02x" % id
print("hname = " + hname)

# Set the mqtt client name
cname = hname
print("cname = " + cname)


# Get the delay to use. pins 10-11 strapped to gnd
wait_delay = get_Delay()
print("delay = %d" % wait_delay)


# define the led to blink when we measure.
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

ds_pin0 = machine.Pin(Pin0,machine.Pin.IN)
ds_sensor0 = ds18x20.DS18X20(onewire.OneWire(ds_pin0))

ds_pin1 = machine.Pin(Pin1,machine.Pin.IN)
ds_sensor1 = ds18x20.DS18X20(onewire.OneWire(ds_pin1))


try:
    roms0 = ds_sensor0.scan()
    roms1 = ds_sensor1.scan()
except:
    led.off();
    machine.soft_reset()

led.off();

network.hostname(hname)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.SSID, config.PSK)


# Connect to the wlan
waitcount = 0
while wlan.status() != 3:
   waitcount+=1
   time.sleep(0.5)
   led.toggle()
   if waitcount > 120:
      led.off()
      machine.reset()

print("WIFI CONNECTED")

#led on when connected to wlan
led.on()
mqc = MQTTClient(cname, config.MQTTHost, 1883)

try:
    mqc.connect()
except:
    led.off();
    machine.soft_reset()

print("MQTT CONNECTED")
led.off();


led.off()
while True:
  led.toggle()
  ds_sensor0.convert_temp()
  led.toggle()
  ds_sensor1.convert_temp()
  led.toggle()
 
  time.sleep_ms(1000)
  led.toggle()

  for rom in roms0:
    T0 = ds_sensor0.read_temp(rom)
    led.toggle()

  for rom in roms1:
    T1 = ds_sensor1.read_temp(rom)
    led.toggle()

  S0 = "{:.1f}".format(T0);
  S1 = "{:.1f}".format(T1);

  print(S0)
  print(S1)

  try:
      mqc.publish(topicT0,S0,True)
      mqc.publish(topicT1,S1,True)
  except:
      led.off();
      machine.soft_reset()

  gc.collect()
  led.off()
  time.sleep(wait_delay)
