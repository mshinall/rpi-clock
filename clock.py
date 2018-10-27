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
weatherLocations = sys.argv[1].split(",")
weatherCityNames = ["" for w in range(0,len(weatherLocations))]
weatherOutlookCt = 4
weatherOutlooks = [["" for w in range(0,weatherOutlookCt)] for z in range(0,len(weatherLocations))]
weatherOutlookIdx = 0
weatherLocationIdx = 0
#degrees = u'\N{DEGREE SIGN}'
degrees = '*'
args = sys.argv[2:]
argIdx = 0
baro = ["steady", "rising", "falling"]
lcdRefreshInt = 1.0
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
	global weatherCityNames, weatherOutlooks, weatherOutlookIdx, weatherLocationIdx
	lcdBuffer(2, weatherCityNames[weatherLocationIdx])
	lcdBuffer(3, weatherOutlooks[weatherLocationIdx][weatherOutlookIdx])

def lcdBuffer(y, string):
	global newLcdBuffer
	newLcdBuffer[y] = list(string.ljust(20)[0:20])

def updateArgBuffer():
	global argIdx, args
	if len(args) > 0:
		lcdBuffer(0, args[argIdx])	

def rotateArg():
	global argIdx, args
	argIdx += 1
	if argIdx >= len(args):
		argIdx = 0
	updateArgBuffer()

def rotateWeather():
	global weatherOutlookIdx, weatherLocations, weatherRotateTimer, weatherLocationIdx, weatherOutlookCt
	weatherOutlookIdx += 1
	if weatherOutlookIdx >= weatherOutlookCt:
		weatherOutlookIdx = 0
		weatherLocationIdx += 1
		if weatherLocationIdx >= len(weatherLocations):
			weatherLocationIdx = 0
	updateWeatherBuffer()

def degrees_to_cardinal(d):
	'''
	note: this is highly approximate...
	'''
	dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
	ix = int((d + 11.25)/22.5)
	return dirs[ix % 16]

def updateWeather():
	global weatherOutlooks, weatherLocations, weatherUpdateTimer, weatherCityNames, baro
	for i in range(0, len(weatherLocations)):
		lookup = weather.lookup(weatherLocations[i])
		condition = lookup.condition
		weatherOutlooks[i][0] = condition.temp + "F " + condition.text
		weatherCityNames[i] = lookup.location.city + lookup.location.region
		#print str(weatherLocations[i]) + ": " + weatherCityNames[i] + ": " + weatherOutlooks[i]
		weatherOutlooks[i][1] = "Wind " + lookup.wind.speed + lookup.units.speed + " " + degrees_to_cardinal(int(lookup.wind.direction)) + " " + lookup.wind.chill + lookup.units.temperature
		weatherOutlooks[i][2] = "Humidity " + lookup.atmosphere.humidity + "%"
		weatherOutlooks[i][3] = "Press " + str(int(float(lookup.atmosphere.pressure))) + lookup.units.pressure + " " + baro[int(lookup.atmosphere.rising)]
	updateWeatherBuffer()

weatherRotateTimer = Timer(2.0, rotateWeather)
weatherUpdateTimer = Timer(1800.0, updateWeather)
argUpdateTimer = Timer(4.0, rotateArg)

try:
	weatherUpdateTimer.start()
	weatherRotateTimer.start()
	argUpdateTimer.start()
	updateWeather()
	updateArgBuffer()
	while True:
		updateTimeBuffer()
		updateLcd()
		time.sleep(lcdRefreshInt)
except:
	clearLcd()
finally:
	weatherUpdateTimer.cancel()
	weatherRotateTimer.cancel()
	argUpdateTimer.cancel()




