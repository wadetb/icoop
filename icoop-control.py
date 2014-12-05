#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, Wade Brainerd
# iCoop is distributed under the terms of the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" 
A GPIO control daemon for controlling the iCoop automated chicken coop.

Home page:
https://github.com/wadetb/icoop2/
"""

import json, os, sqlite3, sys, time

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

OPEN_LIMIT_PIN  = 22
CLOSE_LIMIT_PIN = 23
MOTOR_OPEN_PIN  = 24
MOTOR_CLOSE_PIN = 25

GPIO.setup(MOTOR_OPEN_PIN,  GPIO.OUT)
GPIO.setup(MOTOR_CLOSE_PIN, GPIO.OUT)

GPIO.output(MOTOR_OPEN_PIN, GPIO.LOW)
GPIO.output(MOTOR_CLOSE_PIN, GPIO.LOW)

GPIO.setup(OPEN_LIMIT_PIN,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CLOSE_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

settings = {}

status = { 
    'door': 'close',
    'fail_count': 0,
    'light': 0,
    'temp': 0,
    'humidity': 0
}

def load_settings():
    with sqlite3.connect('icoop.db') as db:
        dbc = db.cursor()
        dbc.execute("SELECT settings FROM settings ORDER BY ts DESC LIMIT 1")
        settings_json = dbc.fetchone()[0]
        try:
            global settings
            settings = json.loads(settings_json)
        except ValueError as err:
            print 'ERROR:', err
        dbc.close()

def report_status():
    if not GPIO.input(OPEN_LIMIT_PIN):
        status['door'] = 'open';
    elif not GPIO.input(CLOSE_LIMIT_PIN):
        status['door'] = 'close';
    else:
        status['door'] = 'unknown';

    with sqlite3.connect('icoop.db') as db:
        dbc = db.cursor()
        dbc.execute("INSERT INTO status (door, light, temp, humidity) VALUES (?, ?, ?, ?)", 
                   (status['door'], status['light'], status['temp'], status['humidity']))
        db.commit()
        dbc.close()

def open_door():
    print "Open door...",
    sys.stdout.flush()

    GPIO.output(MOTOR_CLOSE_PIN, GPIO.LOW)
    time.sleep(0.25)
    GPIO.output(MOTOR_OPEN_PIN, GPIO.HIGH)

    start = time.clock()
    while True:
        time.sleep(0.01)
        if not GPIO.input(OPEN_LIMIT_PIN):
            status['fail_count'] = 0
            print "switch hit"
            break
        if time.clock() - start > 30:
            status['fail_count'] += 1
            print "timeout"
            break

    GPIO.output(MOTOR_OPEN_PIN, GPIO.LOW)

    status['door'] = 'open';
    report_status()
 
def close_door():
    print "Close door...",
    sys.stdout.flush()

    GPIO.output(MOTOR_OPEN_PIN, GPIO.LOW)
    time.sleep(0.25)
    GPIO.output(MOTOR_CLOSE_PIN, GPIO.HIGH)

    start = time.clock()
    while True:
        time.sleep(0.01)
        if not GPIO.input(CLOSE_LIMIT_PIN):
            status['fail_count'] = 0
            print "switch hit"
            break
        if time.clock() - start > 30:
            status['fail_count'] += 1
            print "timeout"
            break

    GPIO.output(MOTOR_CLOSE_PIN, GPIO.LOW)
    report_status()

print "iCoop Control Daemon"
print "Press Ctrl-C to exit."

load_settings()

try:
    while True:
        time.sleep(1)

        if settings['door_mode'] == 'auto':
            pass

        elif settings['door_mode'] == 'open':
            if status['door'] == 'close':
                open_door()

        elif settings['door_mode'] == 'close':
            if status['door'] == 'open':
                close_door()

        try:
            load_settings()
        except IOError:
            pass

except KeyboardInterrupt:
    GPIO.cleanup()

#   light_level = getLightLevel();

#   if (door_mode == DOOR_MODE_AUTO)
#   {
#     if (door_status != DOOR_STATUS_OPENED && light_level > open_light_level)
#     {
#       openDoor();
#     }
#     if (door_status != DOOR_STATUS_CLOSED && light_level < close_light_level)
#     {
#       closeDoor();
#     }
#   }
#   else
#   {
#     if (door_status != DOOR_STATUS_OPENED && door_mode == DOOR_MODE_OPENED)
#     {
#       openDoor();
#     }
#     if (door_status != DOOR_STATUS_CLOSED && door_mode == DOOR_MODE_CLOSED)
#     {
#       closeDoor();
#     }
#   }
  
#   temp = 0;
#   humidity = 0;
#  #if USE_TEMP
#   wdt_reset();
#   if (dht.read())
#   {
# /*
#     int c = ((dht.data[2] & 0x7F) << 8 | dht.data[3]) * ((dht.data[2] & 0x80) ? -1 : 1);
#     int f = c * 9 / 5 + 32;
#     //Serial.print("f:");Serial.println(f);
#     int h = (dht.data[0] << 8) | dht.data[1]; 
#     //Serial.print("h:");Serial.println(h);
#     temp = f;
#     humidity = h;
# */
#     temp = dht.readTemperature(true);
#     humidity = dht.readHumidity();
#   }
# #endif

# #if USE_FAN
#   if (temp >= fan_temp)
#     digitalWrite(FAN_PIN, HIGH);
#   else
#     digitalWrite(FAN_PIN, LOW);
# #endif

# #if USE_HISTORY
#   history_counter++;
#   if (history_counter >= HISTORY_RATE)
#   {
#     light_level_history[history_index] = light_level/4;
#     temp_history[history_index] = temp/4;
#     humidity_history[history_index] = humidity/4;
#     door_status_history[history_index] = door_status;
#     history_index++;
#     if (history_index == HISTORY_COUNT)
#       history_index = 0;
#     history_counter = 0;
#   }
# #endif
