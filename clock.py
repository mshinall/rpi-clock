#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time
import json
import signal
import commands
import RPi.GPIO as GPIO
from threading import _Timer
from weather import Weather, Unit
import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
weather = Weather(unit=Unit.FAHRENHEIT)
weatherLocations = sys.argv[1].split(",")
weatherCityNames = ["" for w in range(0,len(weatherLocations))]
weatherOutlookCt = 4
weatherOutlooks = [["" for w in range(0,weatherOutlookCt)] for z in range(0,len(weatherLocations))]
weatherOutlookIdx = 0
weatherLocationIdx = 0
#degrees = u'\N{DEGREE SIGN}'
degrees = '*'
args = sys.argv[2:]
argIdx = 0
baro = ["steady", "rising", "falling"]
lcdRefreshInt = 1.0
oldLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
newLcdBuffer = [[" " for x in range(0, 20)] for y in range(0,4)]
stopNow = False
showIp = False

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

def updateTimeBuffer():
	now = time.localtime()
	#lcdBuffer(1, time.strftime("%m-%d-%Y  %I:%M %p", now))
	lcdBuffer(1, time.strftime("%Y-%m-%d  %I:%M %p", now))

def updateWeatherBuffer():
	global weatherCityNames, weatherOutlooks, weatherOutlookIdx, weatherLocationIdx
	lcdBuffer(2, weatherCityNames[weatherLocationIdx])
	lcdBuffer(3, weatherOutlooks[weatherLocationIdx][weatherOutlookIdx])

def updateArgBuffer():
	global argIdx, args
	if len(args) > 0:
		lcdBuffer(0, args[argIdx])	

def rotateArg():
	global argIdx, args
	argIdx += 1
	if argIdx >= len(args):
		argIdx = 0
	updateArgBuffer()

def rotateWeather():
	global weatherOutlookIdx, weatherLocations, weatherRotateTimer, weatherLocationIdx, weatherOutlookCt
	weatherOutlookIdx += 1
	if weatherOutlookIdx >= weatherOutlookCt:
		weatherOutlookIdx = 0
		weatherLocationIdx += 1
		if weatherLocationIdx >= len(weatherLocations):
			weatherLocationIdx = 0
	updateWeatherBuffer()

def degrees_to_cardinal(d):
	dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
	ix = int((d + 11.25)/22.5)
	return dirs[ix % 16]

def updateWeather():
	global weatherOutlooks, weatherLocations, weatherUpdateTimer, weatherCityNames, baro
	for i in range(0, len(weatherLocations)):
		lookup = weather.lookup(weatherLocations[i])
		condition = lookup.condition
		weatherOutlooks[i][0] = condition.temp + "F " + condition.text
		weatherCityNames[i] = lookup.location.city + lookup.location.region
		#print str(weatherLocations[i]) + ": " + weatherCityNames[i] + ": " + weatherOutlooks[i]
		weatherOutlooks[i][1] = "Wind " + lookup.wind.speed + lookup.units.speed + " " + degrees_to_cardinal(int(lookup.wind.direction)) + " " + lookup.wind.chill + lookup.units.temperature
		weatherOutlooks[i][2] = "Humidity " + lookup.atmosphere.humidity + "%"
		weatherOutlooks[i][3] = "Baro " + str(int(float(lookup.atmosphere.pressure))) + lookup.units.pressure + " " + baro[int(lookup.atmosphere.rising)]
	updateWeatherBuffer()

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

weatherRotateTimer = Timer(2.0, rotateWeather)
weatherUpdateTimer = Timer(1800.0, updateWeather)
argUpdateTimer = Timer(4.0, rotateArg)


try:
	starting()
	weatherUpdateTimer.start()
	weatherRotateTimer.start()
	argUpdateTimer.start()
	updateWeather()
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
	weatherUpdateTimer.cancel()
	weatherRotateTimer.cancel()
	argUpdateTimer.cancel()
	clearLcd()
	time.sleep(2)
	clearLcd()
	stopping()

