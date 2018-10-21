#!/usr/bin/python

import time
import threading
from weather import Weather, Unit
import I2C_LCD_driver


mylcd = I2C_LCD_driver.lcd()
weather = Weather(unit=Unit.CELSIUS)
weatherLocations = [28350089, 2499644]
weatherCityNames = ["Martinsburg", "Sterling"]
weatherOutlooks = ["", ""]
weatherOutlookIdx = 0;

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd
	mylcd.lcd_display_string(time.strftime("%a, %d %b %Y", time.localtime()), 1, 0)
	mylcd.lcd_display_string(time.strftime("%H:%M:%S", time.localtime()), 2, 0)
	mylcd.lcd_display_string(weatherCityNames[weatherOutlookIdx] + " " + weatherOutlooks[weatherOutlookIdx], 3, 0)

def rotateWeather():
	global weatherOutlookIdx
	weatherOutlookIdx += 1
	if weatherOutlookIdx >= len(weatherLocations):
		weatherOutlookIdx = 0

def updateWeather():
	global outlooks
	for i in range(0, len(weatherLocations)):
		lookup = weather.lookup(weatherLocations[i])
		condition = lookup.condition
		weatherOutlooks[i] = condition.text

try:
	updateWeather()
	updateLcd()
	threading.Timer(600.0, updateWeather).start()
	threading.Timer(60.0, rotateWeather).start()
	while True:
		updateLcd()
		time.sleep(1)
except:
	clearLcd()
