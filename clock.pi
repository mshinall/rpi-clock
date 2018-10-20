#!/usr/bin/python

import sys
import I2C_LCD_driver
from pad4pi import rpi_gpio
import time
import subprocess
import signal
import os
import shlex

MATRIX = [['1', '2', '3', 'A'],
		  ['4', '5', '6', 'B'],
		  ['7', '8', '9', 'C'],
		  ['*', '0', '#', 'D']]

#BCM numbering
#ROWS = [4,17,27,22]
#COLS = [6,13,19,26]
ROWS = [22,27,17,4]
COLS = [26,19,13,6]
MODES = ["FM", "AM"] #, "LSB", "USB"]
FLAGS = ["fm", "am", "lsb", "usb"]
UDP_MODES = ["0", "1", "3", "2"]
UDP_FLAGS = ["N", "M", "L", "U"]
SEEKW = 0.0125
MAX_FREQ = 1700.0000
MIN_FREQ = 25.0000
MAX_FREQ_LENGTH = 9
IN_SAMPLE = 200000
OUT_SAMPLE = 48000
CTL_MODES = ["F", "M", "S", "G", "V"]
GAIN_SETTINGS = ["auto", "0", "9", "14", "27", "37", "77", "87",
				"125", "144", "157", "166", "197", "207", "229",
				"254", "280", "297", "328", "338", "364", "372",
				"386", "402", "421", "434", "439", "445", "480",
				"496"]

freq = 162.4750
inFreq = str(freq)
midx = 0
mode = MODES[midx]
flag = FLAGS[midx]
udpMode = UDP_MODES[midx]
udpFlag = UDP_FLAGS[midx]
edit = False
process1 = 0
process2 = 0
cidx = 0
cmode = CTL_MODES[cidx]
sql = 0
gidx = 0
gain = GAIN_SETTINGS[gidx]
agc = True


mylcd = I2C_LCD_driver.lcd()
factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=MATRIX, row_pins=ROWS, col_pins=COLS)

def freqString():
	return '{:.4f}'.format(freq).rjust(9)

def inFreqFloat():
	try:
		return float(inFreq)
	except:
		return float(inFreq + ".0000")

def clearLcd():
	global mylcd
	mylcd.lcd_clear()

def system(cmd):
	print(cmd)
	os.system(cmd)

def checkFreq():
	global freq
	if freq > MAX_FREQ:
		freq = MAX_FREQ
	elif freq < MIN_FREQ:
		freq = MIN_FREQ

def changeFreq():
	checkFreq()
	updateLcd()
	system(os.getcwd() + "/udpclient.py freq " + str(int(freq * 1000000)))

def startRadio():
	system("amixer set PCM -- 400")
	system("rtl_udp -f " + freqString() + "M -" + udpFlag + " -s " + str(IN_SAMPLE) + " -r " + str(OUT_SAMPLE) + " | aplay -t raw -r " + str(OUT_SAMPLE) + " -f S16_LE -c 1")

def changeMode(step):
	global midx, mode, flag, udpMode, udpFlag

	midx += step
	if midx >= len(MODES):
		midx = 0
	elif midx < 0:
		midx = MODES[len(MODES)-1]

	mode = MODES[midx]
	flag = FLAGS[midx]
	udpMode = UDP_MODES[midx]
	udpFlag = UDP_FLAGS[midx]
	updateLcd()
	system(os.getcwd() + "/udpclient.py mode " + udpMode)

def changeSquelch(step):
	global sql
	sql += step
	updateLcd()
	system(os.getcwd() + "/udpclient.py squelch " + str(int(sql)))

def changeGain(step):
	global gain, gidx
	gidx += step
	if gidx >= len(GAIN_SETTINGS):
		gidx = 0
	elif gidx < 0:
		gidx = GAIN_SETTINGS[len(GAIN_SETTINGS)-1]
	gain = GAIN_SETTINGS[gidx]
	updateLcd()
	system(os.getcwd() + "/udpclient.py gain " + gain)
	if gidx == 0:
		system(os.getcwd() + "/udpclient.py agc on")
	else:
		system(os.getcwd() + "/udpclient.py agc off")

def changeCtlMode():
	global cidx, cmode
	cidx += 1
	if cidx >= len(CTL_MODES):
		cidx = 0
	cmode = CTL_MODES[cidx]
	updateLcd()

def updateLcd():
	clearLcd()
	if edit == True:
		mylcd.lcd_display_string(inFreq, 1, 0)
		mylcd.lcd_display_string("*", 1, 15)
	else:
		mylcd.lcd_display_string(freqString(), 1, 0)
	mylcd.lcd_display_string("MHz", 1, 10)
	mylcd.lcd_display_string(mode, 2, 0)
	mylcd.lcd_display_string("s"+str(sql).zfill(2), 2, 4)
	mylcd.lcd_display_string("g"+gain, 2, 8)
	mylcd.lcd_display_string(cmode, 2, 15)

def numericEntry(key):
	global edit, inFreq
	if edit == False:
		inFreq = ""
	edit = True
	if len(inFreq) < 9:
		inFreq = inFreq + key
	updateLcd()

def decimalEntry(key):
	global edit, inFreq
	edit = True
	if "." not in inFreq:
		inFreq = inFreq + "."
	updateLcd()

def backspaceEntry(key):
	global edit, inFreq, freq
	edit = True
	if len(inFreq) > 0:
		inFreq = inFreq[:len(inFreq) - 1]
	freq = inFreqFloat()
	updateLcd()

def changeFreqEntry(key):
	global edit, freq
	edit = False
	freq = inFreqFloat()
	changeFreq()

def changeModeEntry(key):
	global edit
	edit = False
	#changeMode(1)
	changeCtlMode()

def seekUpEntry(key):
	global edit, freq, inFreq, sql, gain
	edit = False
	if cmode == "F":
		freq = freq + SEEKW
		checkFreq()
		inFreq = freqString()
		changeFreq()
	elif cmode == "M":
		changeMode(1)
	elif cmode == "S":
		changeSquelch(1)
	elif cmode == "G":
		changeGain(1)

def seekDownEntry(key):
	global edit, freq, inFreq, sql, gain
	edit = False
	if cmode == "F":
		freq = freq - SEEKW
		checkFreq()
		inFreq = freqString()
		changeFreq()
	elif cmode == "M":
		changeMode(-1)
	elif cmode == "S":
		changeSquelch(-1)
	elif cmode == "G":
		changeGain(-1)

keyMap = {
	"#": backspaceEntry,
	"*": decimalEntry,
	"A": changeFreqEntry,
	"B": changeModeEntry,
	"C": seekUpEntry,
	"D": seekDownEntry
}

def handleKeyPress(key):
	if key in keyMap:
		handler = keyMap[key]
	else:
		handler = numericEntry
	handler(key);

try:
	checkFreq()
	updateLcd()

	keypad.registerKeyPressHandler(handleKeyPress)

	startRadio()
	"""
	while(True):
		#print("keypad: sleeping...")
		time.sleep(0.2)
	"""
except:
	#print("keypad: cleaning up")
	keypad.cleanup()
	clearLcd()
