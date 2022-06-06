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
import bme280

#
# BME280 Sensor Data
# 
BME280_DEVICE_ID    = 0x77          # BME280 I2C device ID
bme280_sensor   = bme280.BME280Sensor(BME280_DEVICE_ID)

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
    device_id_pos = ow_device.find('28-')
    device_id = ow_device[device_id_pos:]
    lines = ow_sensor_read_temp_raw(ow_device)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = ow_read_temp_raw(ow_device)
    tag_pos = lines[1].find('t=')
    tempf = -999.0
    if tag_pos != -1:
        temp_string = lines[1][tag_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
    return device_id,temp_f

def ow_sensor_read_temp_text(ow_device):
    device_id, femp_f = ow_sensor_read_temp(ow_device)
    out_text = "Soil Temp @{0} : {1:0.1f} F".format(device_id,temp_f)
    return out_text

def ow_sensors_read_all():
    global ow_sensor_temps
    ow_sensor_temps = []
    for ow_device in ow_device_folders:
        device_id, temp_f = ow_sensor_read_temp(ow_device)
        sensor_data = [[device_id,temp_f]]
        ow_sensor_temps.append([device_id,temp_f])

def ow_sensors_report_all():
    global ow_sensor_temps
    for temp_data in ow_sensor_temps:
    #    print('xx:',temp_data)
        device_id, temp_f = temp_data
        report_data('DS18B20 '+device_id,'Soil Temp','{:0.1f} F'.format(temp_f))

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
    report_data('DHT11','Air Temp','{0:0.1f} F'.format(air_temp_f))
    report_data('DHT11','Air Humidity','{0:0.1f} %'.format(air_humidity))

#
#  BME28- Temperature/Humidity/Pressure Sensor Routines
#
def bme280_sensor_read():
    global bme280_chip_id
    global bme280_chip_version
    global bme280_temp_f
    global bme280_humidity
    global bme280_pressure

    (bme280_chip_id,bme280_chip_version) = bme280_sensor.read_id()
    (bme280_temp_c,bme280_pressure,bme280_humidity) = bme280_sensor.read_all()

    bme280_temp_f = ( bme280_temp_c * 9.0 / 5.0 ) + 32.0        # convert C to F
    bme280_pressure = bme280_pressure / 33.863886666667         # convert hPa (hectopascals) to in (inches)

def bme280_sensor_report():
    global bme280_chip_id
    global bme280_chip_version
    global bme280_temp_f
    global bme280_humidity
    global bme280_pressure

    #report_data('BME280','Chip ID','{0}'.format(bme280_chip_id))
    #report_data('BMD280','Chip Version','{0}'.format(bme280_chip_version))

    report_data('BME280','Air Temp','{0:0.1f} F'.format(bme280_temp_f))
    report_data('BME280','Air Humidity','{0:0.1f} %'.format(bme280_humidity))
    report_data('BME280','Air Pressure','{0:0.1f} in Hg'.format(bme280_pressure))


#
# Output Routines
#
def rpad(text,len):
    out_text = text + '                                                                                  '
    out_text = out_text[0:len]
    return out_text

def report_column_header(col_lengths):
    out_text = ''
    col_text = '-----------------------------------------------------------------------------------'
    for col_size in col_lengths:
        out_text = out_text + col_text[0:col_size] + ' '
    return out_text

def report_title():
    print('')
    print('Growtastic Sensors Test - Raspberry Pi Platform')

def report_header():
    print(rpad('Device',30),rpad('Measurement',15),'Reading')
    print(report_column_header([30,15,10]))

def report_data(device,measurement,reading):
    print(rpad(device,30),rpad(measurement,15),reading)

def report_break():
    print(report_column_header([30,15,10]))


#
#  MAIN
#
report_title()

ow_init()                       # Initialize OneWire library

report_header()

while True:
    dht11_sensor_read()         # Read DHT11 Temp/Humidity sensor
    dht11_sensor_report()       # Report DHT11 data

    ow_sensors_read_all()       # Read DS18B20 waterproof temperature sensor(s)
    ow_sensors_report_all()     # Report DS18B20 temperature data

    bme280_sensor_read()        # Read BME280 Temp/Humidiy/Pressure sensor
    bme280_sensor_report()      # Report BME280 data

    time.sleep(5)

    report_break()


