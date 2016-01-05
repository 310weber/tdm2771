#!/usr/bin/python

""" TAOS TMD2771 ALS/prox sensor test program
"""

import sys
from TMD2771 import TMD2771
from time import sleep
from gpiozero import LED
import curses


"""-- Setup --"""
screen = curses.initscr()
menu_scr = curses.newwin(14, 80, 0, 0)
data_scr = curses.newwin(12, 80, 15, 0)
curses.noecho()
curses.curs_set(0)
screen.keypad(1)

menu_scr.box(0, 0)
menu_scr.addstr(2,  2, "Please enter a command...", curses.A_REVERSE)
menu_scr.addstr(4,  4, "d - Get distance")
menu_scr.addstr(5,  4, "l - Get light level")
menu_scr.addstr(6,  4, "s - Stream distance and light data")
menu_scr.addstr(7,  4, "UP - Move forward")
menu_scr.addstr(8,  4, "DOWN - Move backward")
menu_scr.addstr(9,  4, "LEFT - Turn left")
menu_scr.addstr(10, 4, "RIGHT - Turn right")
menu_scr.addstr(11, 4, "q - Exit")

screen.refresh()
menu_scr.refresh()
data_scr.refresh()

key_input = 0
prox_samples = 50
als_samples = 5

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
LED2.off()

sleep(1)

sensor.distance(prox_samples)
sensor.light(als_samples)
sensor.debug = False

"""-- MAIN LOOP --"""
while key_input != ord('q'):

    x = screen.getch()

    if x == ord('d'):
        data_scr.clear()
        data_scr.addstr(2, 2, "The distance is: %d" % sensor.distance(prox_samples))
        data_scr.refresh()
    if x == ord('l'):
        data_scr.clear()
        data_scr.addstr(2, 2, "The light level is: %d lux" % sensor.light(als_samples))
        data_scr.refresh()
    if x == ord('s'):
        y = -1
        data_scr.timeout(1000)
        while y == -1:
            data_scr.clear()
            dist = randrange(0, 1023, 1)
            lux = randrange(0, 200, 1)
            data_scr.addstr(2,2, "Press any key to stop")
            data_scr.addstr(4,2, "Distance: %d, Light: %d" % (dist, lux))
            data_scr.refresh()
            y = data_scr.getch()
        data_scr.timeout(-1)
        data_scr.clear()
        data_scr.refresh()
    if x == curses.KEY_UP:
        data_scr.clear()
        data_scr.addstr(2, 2, "You moved FORWARD")
        data_scr.refresh()
    if x == curses.KEY_DOWN:
        data_scr.clear()
        data_scr.addstr(2, 2, "You moved BACKWARD")
        data_scr.refresh()
    if x == curses.KEY_LEFT:
        data_scr.clear()
        data_scr.addstr(2, 2, "You turned LEFT")
        data_scr.refresh()
    if x == curses.KEY_RIGHT:
        data_scr.clear()
        data_scr.addstr(2, 2, "You turned RIGHT")
        data_scr.refresh()
