# This code reads the values of different atmospheric gases as well as temperature and humidity and stores the readings
# as a .csv file on an sd card for later processing.
# 
# The University of Cape Coast
# 
# Copyright (c) 2022 Jason Appiatu, All rights reserved

# Libraries
from machine import Pin, ADC, SPI
import time
import os
import sdcard


# Initializing SDCard
D5 = 18 # CLK
D6 = 19 # MISO
D7 = 23 # MOSI
# D8 = 5 # CS
D1 = 26 #CS
# Storage spi
storageSpi = SPI(2, baudrate=100000, polarity=1, phase=0, sck=Pin(D5), mosi=Pin(D7), miso=Pin(D6))
# Defining and initializing sdcard
sd = sdcard.SDCard(storageSpi, Pin(D1))
vfs = os.VfsFat(sd) # Creating a virtual storage
# Check if sd card is already mounted
# os.mount(vfs, "/sd")
try:
    os.mount(vfs, "/sd")
except OSError:
    print("OSError")
#     pass

# General filename to save the gas readings
fileName = 'module'

# Creating a variable which will be appended to the filename to make it unique
count = 1
# Creating a constant filename to name the gas file
constFileName = 'module'
# Looping through the files in the root directory to create a unique filename for the gas data.
while True:
#     Checking the root directory for existing filename
    if fileName + '.csv' in os.listdir('/sd/'):
#         Adding a number to the name of the file
        fileName = constFileName + str(count)
    else:
#         Creating a variable called "file" to hold the unique filename. The file is a csv file and can be open with Microsoft excel
        file = "/sd/" + fileName + ".csv"
#         Breaking the loop after getting the filename
        break
#     Increase the count variable by one
    count += 1
    
# Creating pins for the various gases to be read
mq4_1 = ADC(Pin(33))
mq4_2 = ADC(Pin(32))
mq5_1 = ADC(Pin(35))
mq5_2 = ADC(Pin(34))


with open(file, 'w') as module: # Opening the file in appending mode (it could also be open as writable)
    module.write("First MQ4, Second MQ4, First MQ5, Second MQ5") # Writing the types of gases as headings in the file
    module.write("\n") # Writing a new line in the file
    print("First MQ4, Second MQ4, First MQ5, Second MQ5") # Displaying what was written to the file
    
while True: # Looping forever until a break is found
    with open(file, 'a') as module: # Reopening the file to add the values of the data readings in a comma separated format
        # Reading the values of all sensors and storing them in their respective variables
        mq4_1_value = mq4_1.read()
        mq4_2_value = mq4_2.read()
        mq5_1_value = mq5_1.read()
        mq5_2_value = mq5_2.read()

        # Printing the values of the sensors to the console
        print(str(mq4_1_value) + ',' + str(mq4_2_value) + ',' + str(mq5_1_value) + ',' + str(mq5_2_value))
        # Writing the values of the sensors to the file
        module.write("{}, {}, {}, {}".format(mq4_1_value, mq4_2_value, mq5_1_value, mq5_2_value))
        # Writing the values of the sensors to the file
        module.write('\n') # Creating a breakline in the file after every write
    time.sleep(1)
