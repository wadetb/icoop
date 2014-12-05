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
A web server for controlling the iCoop automated chicken coop.

Home page:
https://github.com/wadetb/icoop2/
"""

__version__ = '0.0.1dev'

import json, time

import sqlite3

from flask import Flask, render_template, jsonify
app = Flask(__name__)

settings = {}
status = {}

NO_CONTENT = ('', 204)

def load_settings():
    print "Loading settings..."
    with sqlite3.connect('icoop.db') as db:
        dbc = db.cursor()
        dbc.execute("SELECT settings FROM settings ORDER BY ts DESC LIMIT 1")
        settings_json = dbc.fetchone()[0]
        dbc.close()
    try:
        global settings
        settings = json.loads(settings_json)
    except ValueError as err:
        print 'ERROR:', err
    print "Settings loaded."

def save_settings():
    print "Saving settings..."
    with sqlite3.connect('icoop.db') as db:
        dbc = db.cursor()
        dbc.execute("INSERT INTO settings (settings) VALUES (?)", 
                   (json.dumps(settings),))
        db.commit()
        dbc.close()
    print "Settings saved."

def load_status():
    with sqlite3.connect('icoop.db') as db:
        dbc = db.cursor()
        dbc.execute("SELECT door, light, temp, humidity FROM status ORDER BY ts DESC LIMIT 1")
        result = dbc.fetchone()
        db.commit()
        dbc.close()

    global status
    status = {
        'door': result[0],
        'light': result[1],
        'temp': result[2],
        'humidity': result[3],
    }

@app.route("/status")
def get_status():
    load_status()
    return jsonify({
        'open_light_level': settings['open_light_level'],
        'close_light_level': settings['close_light_level'],
        'door_mode': settings['door_mode'],
        'fan_temp': settings['fan_temp'],
        'door_status': status['door'],
        'light_level': status['light'],
        'temp': status['temp'],
        'humidity': status['humidity'],
    })

@app.route("/set_mode=<mode>")
def set_mode(mode):
    settings['door_mode'] = mode
    save_settings()
    return NO_CONTENT

@app.route("/set_open_light_level=<level>")
def set_open_light_level(level):
    settings['open_light_level'] = level
    save_settings()
    return NO_CONTENT

@app.route("/set_close_light_level=<level>")
def set_close_light_level(level):
    settings['close_light_level'] = level
    save_settings()
    return NO_CONTENT

@app.route("/set_fan_temp=<temp>")
def set_fan_temp(temp):
    settings['fan_temp'] = temp
    save_settings()
    return NO_CONTENT

@app.route("/history")
def get_history():
    history = [['time', 'light', 'tmp', 'hum', 'door']]

    for i in xrange(100):
        history.append([i, 0, 0, 0, 0])

    return jsonify({'table': history})

@app.route("/")
def index():
    return render_template('main.html')

if __name__ == "__main__":
    print "iCoop Webserver"

    load_settings()
    save_settings()

    try:
        app.run(host='0.0.0.0', port=80, debug=True)

    except KeyboardInterrupt:
        pass

