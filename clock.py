#!/usr/bin/python

import time
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
ticker = ["|", "/", "-", "\\"]
t = 0

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, ticker
	t += 1
	if t >= length(ticker):
		t = 0

	mylcd.lcd_display_string("Hello", 1, 1)
	#mylcd.lcd_display_string(time.strftime("%a, %d %b %Y", time.localtime()), 1, 0)
	#mylcd.lcd_display_string(time.strftime("%H:%M:%S", time.localtime()), 2, 0)
	#mylcd.lcd_display_string(ticker[i], 4, 19)

try:
	updateLcd()
	while True:
		time.sleep(0.2)

except:
	clearLcd()
