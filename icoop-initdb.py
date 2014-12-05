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
Script to initialize the iCoop database schema with default values.

Home page:
https://github.com/wadetb/icoop2/
"""

import json, sqlite3

settings = {
    'open_light_level': 700,
    'close_light_level': 600,
    'fan_temp': 80,
    'door_mode': 'auto',
}

print "Initializing iCoop database."

with sqlite3.connect('icoop.db') as db:
    dbc = db.cursor()

    dbc.execute('DROP TABLE settings')
    dbc.execute('DROP TABLE status')

    dbc.execute('''CREATE TABLE settings 
                   (settings text, ts DEFAULT (CURRENT_TIMESTAMP))''')

    dbc.execute("INSERT INTO settings (settings) VALUES (?)", 
               (json.dumps(settings),))

    dbc.execute('''CREATE TABLE status 
                   (door text, light real, temp real, humidity real, ts DEFAULT (CURRENT_TIMESTAMP))''')

    dbc.execute("INSERT INTO status (door, light, temp, humidity) VALUES (?, ?, ?, ?)", 
               ('auto', 0, 0, 0))

    dbc.close()
