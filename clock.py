#!/usr/bin/python

import time
from threading import _Timer
from weather import Weather, Unit
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
weather = Weather(unit=Unit.CELSIUS)
weatherLocations = [28350089, 2499644]
weatherCityNames = ["Martinsburg", "Sterling"]
weatherOutlooks = ["", ""]
weatherOutlookIdx = 0;

oldLcdBuffer = ["", "", "", ""]
newLcdBuffer = ["", "", "", ""]


class Timer(_Timer):
	"""
   def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()
	"""


def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, newLcdBuffer, oldLcdBuffer
	for i in range(0, 3):
		mylcd.lcd_display_string(' ' * len(oldLcdBuffer[i]), i, 0)
		mylcd.lcd_display_string(newLcdBuffer[i], i, 0)
		oldLcdBuffer[i] = newLcdBuffer[i]
		newLcdBuffer[i] = ""

def updateTimeBuffer():
	global newLcdBuffer, oldLcdBuffer
	newLcdBuffer[1] = time.strftime("  %a, %d %b %Y", time.localtime())
	newLcdBuffer[2] = time.strftime("      %H:%M:%S", time.localtime())

def updateWeatherBuffer():
	global newLcdBuffer, oldLcdBuffer
	newLcdBuffer[3] = weatherCityNames[weatherOutlookIdx]
	newLcdBuffer[4] = weatherOutlooks[weatherOutlookIdx]

def rotateWeather():
	global weatherOutlookIdx, weatherLocations, weatherRotateTimer
	weatherOutlookIdx += 1
	if weatherOutlookIdx >= len(weatherLocations):
		weatherOutlookIdx = 0
	updateWeatherBuffer()

def updateWeather():
	global weatherOutlooks, weatherLocations, weatherUpdateTimer
	for i in range(0, len(weatherLocations)):
		lookup = weather.lookup(weatherLocations[i])
		condition = lookup.condition
		weatherOutlooks[i] = condition.text
	updateWeatherBuffer()

weatherRotateTimer = Timer(2.0, rotateWeather)
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
