#!/usr/bin/python

""" TAOS TMD2771 ALS/prox sensor test program
"""

import sys
from TMD2771 import TMD2771
from time import sleep
from gpiozero import LED

"""-- Setup --"""
debug = False
if len(sys.argv) > 1:
    if sys.argv[1] == "debug":  # sys.argv[0] is the filename
        debug = True

# setup ALS/prox sensor
sensor_address = 0x39
sensor = TMD2771()
sensor.debug = True
sensor.start()

# Set output pin numbers for LEDS
LED1 = LED(17)
LED1.off()
LED2 = LED(27)
LED2.on()

sleep(1)

sensor.get_distance()
sensor.get_ambient_light()
sensor.debug = False

"""-- MAIN LOOP --"""
while True:
    print "Distance is: %d; Light is: %d lux" % (sensor.get_distance(), sensor.get_ambient_light())
    LED1.toggle()
    LED2.toggle()
    sleep(1)
