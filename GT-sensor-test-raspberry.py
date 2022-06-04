#!/usr/bin/python3
# GT-sensor-test-raspberry.py
#
# Description:
#	Growtacular Sensors Test for RaspberryPi platform
#
#	Tests the following sensors:
#    	o DS18B20 temperature sensor(s), one or more connected in parallel
#    	o DHT11 temperature and pressure sensor
#    	o xxx Capacitive soil moisture sensor
#
# Compatibility:
#   RaspberryPi-3B/1GB
#
# Copyright:
#	Copyright (c) 2022 Kurt Schulte
#
# History:
#	01.00.00  2022.06.03  KSchulte  	Original version
#

import sys
import Adafruit_DHT
import os
import glob
import time

#
# DHT11 Sensor Data
#

DHT11_PIN = 17

#
# OneWire Sensors Data
#
ow_base_dir = '/sys/bus/w1/devices/'
ow_device_folders = glob.glob(ow_base_dir + '28*')
ow_device_count = len(ow_device_folders)
ow_device_temps = []

#
# OneWire Routines
# 

def ow_init():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    ow_get_devices()

def ow_get_devices():
    global ow_device_folders
    global ow_device_count

    ow_device_folders = glob.glob(ow_base_dir + '28*')
    ow_device_count = len(ow_device_folders)

def ow_sensor_read_temp_raw(ow_device):
    ow_device_file = ow_device + '/w1_slave'
    f = open(ow_device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def ow_sensor_read_temp(ow_device):
    lines = ow_sensor_read_temp_raw(ow_device)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = ow_read_temp_raw(ow_device)
    equals_pos = lines[1].find('t=')
    tempf = -999.0
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

def ow_sensor_read_temp_text(ow_device):
    temp_f = ow_sensor_read_temp(ow_device)
    device_id_pos = ow_device.find('28-')
    device_id = ow_device[device_id_pos:]
    out_text = "Soil Temp @{0} : {1:0.1f} F".format(device_id,temp_f)
    return out_text

def ow_sensors_read_all():
    global ow_sensor_temps
    ow_sensor_temps = []
    for ow_device in ow_device_folders:
        temp_text = ow_sensor_read_temp_text(ow_device)
        ow_sensor_temps.append(temp_text)

def ow_sensors_report_all():
    global ow_sensor_temps
    for temp_text in ow_sensor_temps:
        print(temp_text)

#
#  DHT11 Routines
# 
def dht11_sensor_read():
    global air_humidity
    global air_temp_f
    air_humidity, air_temp_c = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11,DHT11_PIN)
    air_temp_f = ( air_temp_c * 9.0 / 5.0 ) + 32.0

def dht11_sensor_report():
    global air_temp_f
    global air_humidity
    print('Air Temp                   : {0:0.1f} F'.format(air_temp_f))
    print('Air Humidity               : {0:0.1f} %'.format(air_humidity))

#
#  MAIN
#

print('Growtastic Sensors Test - Raspberry Pi Platform')

ow_init()                   # Initialize OneWire library

while True:
    dht11_sensor_read()
    dht11_sensor_report()

    ow_sensors_read_all()
    ow_sensors_report_all()

    time.sleep(5)

    print ('----------------------------')

