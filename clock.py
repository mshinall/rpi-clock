#!/usr/bin/python

import time
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
ticker = ["|", "/", "-"] #, "\\"]
t = 0

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, ticker, t
	t += 1
	if t >= len(ticker):
		t = 0
	"""
	mylcd.lcd_display_string("Hello", 1, 1)
	"""
	mylcd.lcd_display_string(time.strftime("%a, %d %b %Y", time.localtime()), 1, 0)
	mylcd.lcd_display_string(time.strftime("%H:%M:%S", time.localtime()), 2, 0)
	mylcd.lcd_display_string(ticker[t], 4, 19)

try:
	updateLcd()
	while True:
		time.sleep(0.2)
except:
	clearLcd()
