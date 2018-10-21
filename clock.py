#!/usr/bin/python

import time
from weather import Weather, Unit
import I2C_LCD_driver


mylcd = I2C_LCD_driver.lcd()
weather = Weather(unit=Unit.CELSIUS)
wlocs = [28350089, 2499644]
wnames = ["Martinsburg", "Sterling"]
w = 0
wl = 0
outlooks = ["", ""]

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, w, wl, wlocs
	w += 1
	wl += 1
	if w >= 599:
		updateWeather()
		w = 0
		if wl >= len(wlocs):
			wl = 0

	mylcd.lcd_display_string(time.strftime("%a, %d %b %Y", time.localtime()), 1, 0)
	mylcd.lcd_display_string(time.strftime("%H:%M:%S", time.localtime()), 2, 0)
	mylcd.lcd_display_string(wnames[wl] + " " + outlooks[wl], 3, 0)

def updateWeather():
	global outlooks
	for i in range(0, len(wlocs)):
		lookup = weather.lookup(wlocs[i])
		condition = lookup.condition
		outlooks[i] = condition.text

try:
	updateWeather()
	updateLcd()
	while True:
		updateLcd()
		time.sleep(1)
except:
	clearLcd()
