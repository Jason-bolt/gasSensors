# This code reads the values of different atmospheric gases as well as temperature and humidity and stores the readings
# as a .csv file on an sd card for later processing.
# 
# The University of Cape Coast
# 
# Copyright (c) 2022 Jason Appiatu, All rights reserved


#Libraries
from machine import Pin, ADC, I2C, SPI
import time
# CCS811 is an external library. It can be downloaded from https://github.com/Notthemarsian/CCS811/blob/master/CCS811.py
from CCS811 import CCS811
import sdcard
import os
from sht3x import SHT3X

# General filename to save the gas readings
fileName = 'gasData'

# Creating a variable which will be appended to the filename to make it unique
count = 1
# Creating a constant filename to name the gas file
constFileName = 'gasData'
# Looping through the files in the root directory to create a unique filename for the gas data.
while True:
#     Checking the root directory for existing filename
    if fileName + '.csv' in os.listdir('/'):
#         Adding a number to the name of the file
        fileName = constFileName + str(count)
    else:
#         Creating a variable called "file" to hold the unique filename. The file is a csv file and can be open with Microsoft excel
        file = "/" + fileName + ".csv"
#         Breaking the loop after getting the filename
        break
#     Increase the count variable by one
    count += 1

# Creating an i2c object with of the I2C class
i2c = I2C(1, sda=Pin(21), scl=Pin(22))
# Instantiating the CCS811 library with i2c
ccs811 = CCS811(i2c)

# time.sleep(1)

# Creating pins for the various gases to be read
co = ADC(Pin(36))
nh3 = ADC(Pin(34))
no2 = ADC(Pin(35))
windSpeedPin = Pin(16, Pin.IN)
windSpeed = 0.0
hydrogen = ADC(Pin(33))
methane = ADC(Pin(32))
o2 = ADC(Pin(39))


# Defining the function to measure the temperature and humidity using i2c communication at 0x44
def measure(i2c):  
    i2c.writeto(0x44, b'\x2C\x10') # The SHT3x module being used has the address 0x44
    data = i2c.readfrom(0x44, 6) 
    
    aux = (data[0] << 8 | data[1]) * 175
    t_int = (aux // 0xffff) - 45;
    t_dec = (aux % 0xffff * 100) // 0xffff
    aux = (data[3] << 8 | data[4]) * 100
    h_int = aux // 0xffff
    h_dec = (aux % 0xffff * 100) // 0xffff
    return t_int, t_dec, h_int, h_dec


# A function to map the upper and lower values to defined values
# This function may not used
def mapValue(analogValue, actualLow, actualHigh, myLow, myHigh):
    if analogValue == 0:
        return myLow
    else:
        value = analogValue / actualHigh
        value = value * myHigh
        return value


# Function to calculate the windspeed using the hall effect sensor
# This function counts the number of times the magnet under the blade of the anemomter passes over a particular point using a hall effect sensor
def calcWind():    
    #  Diameter of the wind vane in mm
    vane_diameter = 120
    #  Calculating the vane circumference
    vane_circ = ((vane_diameter * 1.000) / 1000) * 3.1415
    #  Vane inefficiency factor (Should come from a comparison with a working vane)
    err = 700.5

    rotations = 0
    trigger = 0
    count = 0
    sensorValue = 0
    rots_per_second = 0.0

#     Sampling for 6000 miliseconds or 6 seconds
    while (count < 6000):
        sensorValue = windSpeedPin.value() # Reading the state of the pin. 
        if sensorValue == 1 and trigger == 0:
            rotations = rotations + 1
            trigger = 1
        if sensorValue == 0:
            trigger = 0
        count = count + 1
        time.sleep_ms(1)
    if rotations == 1 and sensorValue == 1:
        rotations = 0
    
    rots_per_second = (rotations * 1.000) / 6000
    windspeed = rots_per_second * vane_circ * err
    #  Serial.print("Windspeed is ");
#     print(windspeed)
    #  Serial.println(" m/s");
    count = 0
    rotations = 0

    return windspeed


# Beginning of the main code and implementation of the functions
try:
    print("starting...")
    with open(file, 'a') as gasDataFile: # Opening the file in appending mode (it could also be open as writable)
        gasDataFile.write("eCO2, TVOC, CO, NH3, NO2, Hydrogen(MQ5), Methane(MQ4), Humidity, Temperature, Wind speed") # Writing the types of gases as well as temperature and humidity as headings in the file
        gasDataFile.write("\n") # Writing a new line in the file
        print("eCO2, TVOC, CO, NH3, NO2, Hydrogen(MQ5), Methane(MQ4), Humidity, Temperature, Wind speed") # Displaying what was written to the file
    
    while True: # Looping forever until a break is found
        try: # This works with the except statement to catch any errors that may come up
            with open(file, 'a') as gasDataFile: # Reopening the file to add the values of the data readings in a comma separated format
                if ccs811.data_ready(): # Checking if the CCS811 module is ready
                    
                    # Reading the values of all sensors and storing them in their respective variables
                    coValue = co.read()
                    nh3Value = nh3.read()
                    o2Value = o2.read()
                    no2Value = no2.read()
                    co2Value = str(ccs811.eCO2)
                    tvocValue = str(ccs811.tVOC)
                    hydrogenValue = hydrogen.read()
                    methaneValue = methane.read()
                    measurement = measure(i2c)
                    temp = str(measurement[0]) + '.' + str(measurement[1])
                    humid = str(measurement[2]) + '.' + str(measurement[3])
                    windSpeed = calcWind()
                    
                    # Printing the values of the sensors to the console
#                     print("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(co2Value, tvocValue, coValue, nh3Value, no2Value, hydrogenValue, methaneValue, temp, humid, windSpeed, o2Value))
                    print("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(co2Value, tvocValue, coValue, nh3Value, no2Value, hydrogenValue, methaneValue, temp, humid, windSpeed))
                    
#                     values = str(co2Value)+','+str(tvocValue)+','+str(coValue)+','+str(nh3Value)+','+str(no2Value)+','+str(hydrogenValue)+','+str(methaneValue)+','+str(temp)+','+str(humid)+','+str(windSpeed)+','+str(o2Value)
                    
                    # Writing the values of the sensors to the file    
#                     gasDataFile.write("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(co2Value, tvocValue, coValue, nh3Value, no2Value, hydrogenValue, methaneValue, temp, humid, windSpeed, o2Value))
                    gasDataFile.write("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(co2Value, tvocValue, coValue, nh3Value, no2Value, hydrogenValue, methaneValue, temp, humid, windSpeed))
                    
            #         CJMCU-6814
#                     coValue = mapValue(co.read(), 0, 4095, 1, 1000)
#                     nh3Value = mapValue(nh3.read(), 0, 4095, 1, 500)
#                     no2Value = mapValue(no2.read(), 0, 4095, 5, 1000)
                    
                    gasDataFile.write("\n") # Creating a breakline in the file after every write
                   
        except OSError: # Catching any OS error. This can arise from the CCS811 library
            print("OSError") # Printing that an OSError occured and continuing
        time.sleep(1) # Waiting for 1 second
        
except KeyboardInterrupt: # To detect when Ctrl + C is pressed
    print("Ending...") # 'Ending...' is printed to the console and the program ends



