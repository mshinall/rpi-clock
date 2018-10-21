#!/usr/bin/python

import time
import json
from threading import _Timer
from weather import Weather, Unit
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
weather = Weather(unit=Unit.FAHRENHEIT)
weatherLocations = [28350089, 2499644]
weatherCityNames = ["Martinsburg", "Sterling"]
weatherOutlooks = ["", ""]
weatherOutlookIdx = 0;

oldLcdBuffer = ["", "", "", ""]
newLcdBuffer = ["", "", "", ""]


class Timer(_Timer):
   def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, newLcdBuffer, oldLcdBuffer
	for i in range(0, 4):
		if oldLcdBuffer[i] != newLcdBuffer[i]:
			if i > 1:
				mylcd.lcd_display_string(' ' * len(oldLcdBuffer[i]), i+1, 0)
			mylcd.lcd_display_string(newLcdBuffer[i], i+1, 0)
			oldLcdBuffer[i] = newLcdBuffer[i]

def updateTimeBuffer():
	global newLcdBuffer, oldLcdBuffer
	now = time.localtime()
	newLcdBuffer[0] = time.strftime("  %a, %d %b %Y", now)
	newLcdBuffer[1] = time.strftime("      %H:%M:%S", now)

def updateWeatherBuffer():
	global newLcdBuffer, oldLcdBuffer, weatherCityNames, weatherOutlooks, weatherOutlookIdx
	newLcdBuffer[2] = weatherCityNames[weatherOutlookIdx]
	newLcdBuffer[3] = weatherOutlooks[weatherOutlookIdx]

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
		weatherOutlooks[i] = condition.temp + "°F " + condition.text
		print str(weatherLocations[i]) + ": " + weatherCityNames[i] + ": " + weatherOutlooks[i]
	updateWeatherBuffer()

weatherRotateTimer = Timer(5.0, rotateWeather)
weatherUpdateTimer = Timer(600.0, updateWeather)

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
