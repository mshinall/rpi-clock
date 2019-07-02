#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import json
import signal
import commands
import RPi.GPIO as GPIO
from threading import _Timer
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
args = sys.argv[1:]
argIdx = 0
lcdRefreshInt = 1.0
oldLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
newLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
stopNow = False
showIp = False
showTimeSep = True
showUpdWthr = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def buttonCallback(channel):
	global showIp
	print(time.strftime("%c", time.localtime()) + " button pushed")
	showIp = True

GPIO.add_event_detect(20, GPIO.FALLING, callback=buttonCallback)

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

def lcdBuffer(y, string):
	global newLcdBuffer
	newLcdBuffer[y] = list(string.ljust(20)[0:20])

#printBuffers()

def clearLcd():
	global mylcd, oldLcdBuffer, newLcdBuffer
	oldLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
	newLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
	updateLcd()
	mylcd.lcd_clear()

def updateLcd():
	global mylcd, newLcdBuffer, oldLcdBuffer
	#printBuffers()
	for y in range(0, 4):
		for x in range(0, 20):
			if oldLcdBuffer[y][x] != newLcdBuffer[y][x]:
				mylcd.lcd_display_string(newLcdBuffer[y][x], y+1, x)
				oldLcdBuffer[y][x] = newLcdBuffer[y][x]

def rightJustify(str):
	while(len(str) < 20):
        	str = " " + str
	return str

def centerJustify(str):
	while(len(str) < 20):
		str = " " + str + " "
	return str

def updateTimeBuffer():
	global showTimeSep
	now = time.localtime()
	lcdBuffer(0, time.strftime("%A", now))
	lcdBuffer(1, rightJustify(time.strftime("%B %d %Y", now)))
	if showTimeSep == True:
		showTimeSep = False
		lcdBuffer(2, centerJustify(time.strftime("%I:%M:%S %p", now)))
	else:
		showTimeSep = True
		lcdBuffer(2, centerJustify(time.strftime("%I %M %S %p", now)))

def updateArgBuffer():
	global argIdx, args
	if len(args) > 0:
		lcdBuffer(3, args[argIdx])

def rotateArg():
	global argIdx, args
	argIdx += 1
	if argIdx >= len(args):
		argIdx = 0
	updateArgBuffer()

def showIpAddress():
	global mylcd, showIp
	clearLcd()
	mylcd.backlight(1)
	myip = commands.getoutput("hostname -I")
	lcdBuffer(1, "ip address")
	lcdBuffer(2, myip.split()[0])
	updateLcd()
	time.sleep(2)
	showIp = False

def stop():
	global stopNow
	stopNow = True
	sys.exit(0)

def starting():
	print(time.strftime("%c", time.localtime()) + " starting")
	global mylcd
	clearLcd()
	mylcd.backlight(1)
	myip = commands.getoutput("hostname -I")
	lcdBuffer(1, "starting up...")
	updateLcd()
	time.sleep(2)

def stopping():
	print(time.strftime("%c", time.localtime()) + " stopping")
	global mylcd
	clearLcd()
	lcdBuffer(1, "shutting down...")
	updateLcd()
	time.sleep(2)
	clearLcd()
	mylcd.backlight(0)

argUpdateTimer = Timer(lcdRefreshInt, rotateArg)

try:
	starting()
	argUpdateTimer.start()
	updateArgBuffer()

	signal.signal(signal.SIGINT, stop)
	signal.signal(signal.SIGTERM, stop)
	signal.signal(signal.SIGABRT, stop);
	signal.signal(signal.SIGQUIT, stop);

	while True:
		if showIp == True:
			showIpAddress()
		if stopNow == True:
			break
		updateTimeBuffer()
		updateLcd()
		time.sleep(lcdRefreshInt)
except:
	print(time.strftime("%c", time.localtime()) + " exception in main loop")
	clearLcd()
finally:
	GPIO.cleanup()
	argUpdateTimer.cancel()
	clearLcd()
	time.sleep(2)
	clearLcd()
	stopping()
