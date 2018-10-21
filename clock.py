#!/usr/bin/python

import time
from weather import Weather, Unit
import I2C_LCD_driver


mylcd = I2C_LCD_driver.lcd()
weather = Weather(unit=Unit.CELSIUS)
w = 0
outlook = ""

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, ticker, w, q
	w += 1
	if w >= 599:
		updateWeather()
		w = 0

	mylcd.lcd_display_string(time.strftime("%a, %d %b %Y", time.localtime()), 1, 0)
	mylcd.lcd_display_string(time.strftime("%H:%M:%S", time.localtime()), 2, 0)
	mylcd.lcd_display_string(outlook, 3, 0)

def updateWeather():
	global outlook
	lookup = weather.lookup(28350089)
	condition = lookup.condition
	outlook = condition.text

try:
	updateWeather()
	updateLcd()
	while True:
		updateLcd()
		time.sleep(1)
except:
	clearLcd()
