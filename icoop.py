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
https://github.com/wadetb/icoop/
"""

__version__ = '0.0.1dev'

import json

from flask import Flask, render_template, jsonify
app = Flask(__name__)

settings = {
    'open_light_level': 700,
    'close_light_level': 600,
    'fan_temp': 80,
    'door_mode': 'auto',
}

no_content = ('', 204)

def load_settings():
    with open('settings.json') as settings_file:
        global settings
        settings = json.load(settings_file)

def save_settings():
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file)

@app.route("/status")
def status():
    status = {
        'open_light_level': settings['open_light_level'],
        'close_light_level': settings['close_light_level'],
        'door_mode': settings['door_mode'],
        'fan_temp': settings['fan_temp'],
        'light_level': 0,
        'temp': 0,
        'door_status': 'The door is open',
    }

    return jsonify(status)

@app.route("/set_mode=<mode>")
def set_door_mode(mode):
    settings['door_mode'] = mode
    save_settings()
    return no_content

@app.route("/set_open_light_level=<level>")
def set_open_light_level(level):
    settings['open_light_level'] = level
    save_settings()
    return no_content

@app.route("/set_close_light_level=<level>")
def set_close_light_level(level):
    settings['close_light_level'] = level
    save_settings()
    return no_content

@app.route("/set_fan_temp=<temp>")
def set_fan_temp(temp):
    settings['fan_temp'] = temp
    save_settings()
    return no_content

@app.route("/history")
def history():
    history = [['time', 'light', 'tmp', 'hum', 'door']]
    
    for i in xrange(100):
        history.append([i, 0, 0, 0, 0])

    return jsonify({'table': history})

@app.route("/")
def index():
    templateData = {
        'x' : 'x',
    }
    return render_template('main.html', **templateData)

if __name__ == "__main__":
    try:
        load_settings()
    except IOError:
        # Initialize settings file with defaults.
        save_settings()

    app.run(host='0.0.0.0', port=80, debug=True)
