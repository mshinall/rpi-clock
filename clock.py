#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
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
args = sys.argv[1:]
argIdx = 0

oldLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
newLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]

print(json.dumps(sys.argv))

class Timer(_Timer):
   def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()

def printBuffers():
	global newLcdBuffer, oldLcdBuffer
	for i in range(0, 4):
		print(str(i) + " " + json.dumps(oldLcdBuffer[i]) + ">" + json.dumps(newLcdBuffer[i]))
	print("")

#printBuffers() 

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

"""
def updateLcd():
	printBuffers()
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
	#printBuffers()
	for y in range(0, 4):
		for x in range(0, 20):
			if oldLcdBuffer[y][x] != newLcdBuffer[y][x]:
				mylcd.lcd_display_string(newLcdBuffer[y][x], y+1, x)
				oldLcdBuffer[y][x] = newLcdBuffer[y][x]

def updateTimeBuffer():
	now = time.localtime()
	lcdBuffer(1, time.strftime("%m/%d/%Y  %I:%M %p", now))

def updateWeatherBuffer():
	global weatherCityNames, weatherOutlooks, weatherOutlookIdx
	lcdBuffer(2, weatherCityNames[weatherOutlookIdx])
	lcdBuffer(3, weatherOutlooks[weatherOutlookIdx])

def lcdBuffer(y, string):
	global newLcdBuffer
	newLcdBuffer[y] = list(string.ljust(20)[0:20])

def updateArgBuffer():
	global argIdx, args
	lcdBuffer(0, args[argIdx])	

def rotateArg():
	global argIdx, args
	argIdx += 1
	if argIdx >= len(args):
		argIdx = 0
	updateArgBuffer()

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
argUpdateTimer = Timer(2.0, rotateArg)

try:
	weatherUpdateTimer.start()
	weatherRotateTimer.start()
	argUpdateTimer.start()
	updateWeather()
	updateArgBuffer()
	while True:
		updateTimeBuffer()
		updateLcd()
		time.sleep(1)
except:
	clearLcd()
finally:
	weatherUpdateTimer.cancel()
	weatherRotateTimer.cancel()
	argUpdateTimer.cancel()




