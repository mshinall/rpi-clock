#!/usr/bin/python

import time
import weather
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
weather = weather.Weather(unit=weather.Unit.CELSIUS)
w = 0;
condition = "";

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, ticker, w
	w += 1
	if w >= 599:
		updateWeather()
		w = 0
	"""
	mylcd.lcd_display_string("Hello", 1, 1)
	"""
	mylcd.lcd_display_string(time.strftime("%a, %d %b %Y", time.localtime()), 1, 0)
	mylcd.lcd_display_string(time.strftime("%H:%M:%S", time.localtime()), 2, 0)
	mylcd.lcd_display_string(condition.text, 3, 0)

def updateWeather():
	global condition
	lookup = weather.lookup(560743)
	condition = lookup.condition

print(condition.text)

try:
	updateWeather()
	updateLcd()
	while True:
		updateLcd()
		time.sleep(1)
except:
	clearLcd()
