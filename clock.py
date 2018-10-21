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
	mylcd.lcd_display_string(time.strftime("  %a, %d %b %Y", time.localtime()), 1, 0)
	mylcd.lcd_display_string(time.strftime("      %H:%M:%S", time.localtime()), 2, 0)
	mylcd.lcd_display_string(weatherCityNames[weatherOutlookIdx], 3, 0)
	mylcd.lcd_display_string(weatherOutlooks[weatherOutlookIdx], 4, 0)

def clearLcdWeather():
	global mylcd
	mylcd.lcd_display_string("                    ", 3, 0)
	mylcd.lcd_display_string("                    ", 4, 0)

def rotateWeather():
	global weatherOutlookIdx, weatherLocations
	weatherOutlookIdx += 1
	if weatherOutlookIdx >= len(weatherLocations):
		weatherOutlookIdx = 0
	clearLcdWeather()

def updateWeather():
	global weatherOutlooks, weatherLocations
	for i in range(0, len(weatherLocations)):
		lookup = weather.lookup(weatherLocations[i])
		condition = lookup.condition
		weatherOutlooks[i] = condition.text
	clearLcdWeather()

weatherUpdateTimer = threading.Timer(600.0, updateWeather)
weatherRotateTimer = threading.Timer(2.0, rotateWeather)

try:
	weatherUpdateTimer.start()
	weatherRotateTimer.start()
	updateWeather()
	while True:
		updateLcd()
		time.sleep(1)
except:
	clearLcd()
finally:
	weatherUpdateTimer.cancel()
	weatherRotateTimer.cancel()
