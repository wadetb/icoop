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
I2C control daemon for controlling the iCoop automated chicken coop.

Home page:
https://github.com/wadetb/icoop2/
"""

import datetime, json, os, sqlite3, sys, time

import logging
import sys
log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

db = sqlite3.connect('icoop.db')

import smbus
bus = smbus.SMBus(1)
address = 0x04

OPEN_DOOR_CMD       = 1
CLOSE_DOOR_CMD      = 2
GET_DOOR_STATUS_CMD = 3
GET_LIGHT_LEVEL_CMD = 4
GET_TEMP_CMD        = 5
GET_HUMIDITY_CMD    = 6

DOOR_OPEN           = 1
DOOR_CLOSE          = 2
DOOR_UNKNOWN        = 3

settings = {}

status = { 
    'door': 'close',
    'fail_count': 0,
    'light': 0,
    'temp': 0,
    'humidity': 0
}

def load_settings():
    dbc = db.cursor()
    dbc.execute("SELECT settings FROM settings ORDER BY ts DESC LIMIT 1")
    settings_json = dbc.fetchone()[0]
    try:
        global settings
        settings = json.loads(settings_json)
    except ValueError as err:
        log.error(err)
    dbc.close()

def i2c_cmd(cmd):
    bus.write_byte(address, cmd)
    result = bus.read_byte(address)
    #print "i2c_cmd", cmd, "=", result
    return result

def refresh_status():
    d = i2c_cmd(GET_DOOR_STATUS_CMD)
    status['door'] = { DOOR_OPEN: 'open', DOOR_CLOSE: 'close', DOOR_UNKNOWN: 'unknown' }[d]
    status['light'] = i2c_cmd(GET_LIGHT_LEVEL_CMD) * 4
    status['temp'] = i2c_cmd(GET_TEMP_CMD)
    status['humidity'] = i2c_cmd(GET_HUMIDITY_CMD)

def report_status():
    dbc = db.cursor()
    dbc.execute("DELETE FROM status WHERE 1=1")
    dbc.execute("INSERT INTO status (door, light, temp, humidity) VALUES (?, ?, ?, ?)", 
               (status['door'], status['light'], status['temp'], status['humidity']))
    db.commit()
    dbc.close()

def report_history():
    dbc = db.cursor()
    dbc.execute("INSERT INTO history (door, light, temp, humidity) VALUES (?, ?, ?, ?)", 
               (status['door'], status['light'], status['temp'], status['humidity']))
    db.commit()
    dbc.close()
    log.info("History recorded.")

def open_door():
    log.info("Open door...")
    i2c_cmd(OPEN_DOOR_CMD)
 
def close_door():
    log.info("Close door...")
    i2c_cmd(CLOSE_DOOR_CMD)

log.info("iCoop I2C Control Daemon")
log.info("Press Ctrl-C to exit.")

history_timer = datetime.timedelta(minutes=15)
last_history_time = datetime.datetime.now()

load_settings()
refresh_status()
report_history()

try:
    while True:
        time.sleep(1)

        load_settings()
        refresh_status()

        #print settings
        #print status

        if settings['door_mode'] == 'auto':
            if int(status['light']) > int(settings['open_light_level']):
                if status['door'] == 'close':
                    open_door()
                    report_history()

            elif int(status['light']) < int(settings['close_light_level']):
                if status['door'] == 'open':
                    close_door()
                    report_history()

        elif settings['door_mode'] == 'open':
            if status['door'] == 'close':
                open_door()
                report_history()

        elif settings['door_mode'] == 'close':
            if status['door'] == 'open':
                close_door()
                report_history()

        report_status()

        if datetime.datetime.now() - last_history_time > history_timer:
            last_history_time = datetime.datetime.now()
            report_history()

except KeyboardInterrupt:
    pass
