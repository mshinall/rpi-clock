#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
from threading import _Timer
from weather import Weather, Unit
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
weather = Weather(unit=Unit.FAHRENHEIT)
weatherLocations = [28350089, 2499644, 2409835, 2428344]
weatherCityNames = ["Martinsburg WV", "Sterling VA", "Germantown MD", "Jacksonville FL"]
weatherOutlooks = ["", "", "", ""]
weatherOutlookIdx = 0;
#degrees = u'\N{DEGREE SIGN}'
degrees = '*'

oldLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
newLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]

class Timer(_Timer):
   def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

"""
def updateLcd():
	global mylcd, newLcdBuffer, oldLcdBuffer
	for i in range(0, 4):
		if oldLcdBuffer[i] != newLcdBuffer[i]:
			if i > 1:
				mylcd.lcd_display_string(' ' * len(oldLcdBuffer[i]), i+1, 0)
			mylcd.lcd_display_string(newLcdBuffer[i], i+1, 0)
			oldLcdBuffer[i] = newLcdBuffer[i]
"""

def updateLcd():
	global mylcd, newLcdBuffer, oldLcdBuffer
	for y in range(0, 4):
		for x in range(0, 20):
			if oldLcdBuffer[y][x] != newLcdBuffer[y][x]:
				mylcd.lcd_display_string(newLcdBuffer[y][x], y+1, x)
				oldLcdBuffer[y][x] = newLcdBuffer[y][x]

def updateTimeBuffer():
	now = time.localtime()
	lcdBuffer(0, time.strftime("  %a, %d %b %Y", now))
	lcdBuffer(1, time.strftime("    %I:%M:%S %p", now))

def updateWeatherBuffer():
	global weatherCityNames, weatherOutlooks, weatherOutlookIdx
	lcdBuffer(2, weatherCityNames[weatherOutlookIdx])
	lcdBuffer(3, weatherOutlooks[weatherOutlookIdx])

def lcdBuffer(y, string):
	global newLcdBuffer
	newLcdBuffer[y] = [list(string.ljust(20))]

def rotateWeather():
	global weatherOutlookIdx, weatherLocations, weatherRotateTimer
	weatherOutlookIdx += 1
	if weatherOutlookIdx >= len(weatherLocations):
		weatherOutlookIdx = 0
	updateWeatherBuffer()

def updateWeather():
	global weatherOutlooks, weatherLocations, weatherUpdateTimer, weatherCityNames
	for i in range(0, len(weatherLocations)):
		lookup = weather.lookup(weatherLocations[i])
		condition = lookup.condition
		weatherOutlooks[i] = condition.temp + "F " + condition.text
		print str(weatherLocations[i]) + ": " + weatherCityNames[i] + ": " + weatherOutlooks[i]
	updateWeatherBuffer()

weatherRotateTimer = Timer(5.0, rotateWeather)
weatherUpdateTimer = Timer(1800.0, updateWeather)

try:
	weatherUpdateTimer.start()
	weatherRotateTimer.start()
	updateWeather()
	while True:
		updateTimeBuffer()
		updateLcd()
		time.sleep(1)
except:
	clearLcd()
finally:
	weatherUpdateTimer.cancel()
	weatherRotateTimer.cancel()
