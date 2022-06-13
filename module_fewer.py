# This code reads the values of different atmospheric gases notably hydrogen and methane
# as a .csv file on an sd card for later processing.
# 
# The University of Cape Coast
# 
# Copyright (c) 2022 Jason Appiatu, All rights reserved

# Libraries
from machine import Pin, ADC
import time
import os

# General filename to save the gas readings
fileName = 'module'

# Creating a variable which will be appended to the filename to make it unique
count = 1
# Creating a constant filename to name the gas file
constFileName = 'module'
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
    
# Creating pins for the various gases to be read
mq4 = ADC(Pin(33))
mq5 = ADC(Pin(32))

with open(file, 'w') as module: # Opening the file in appending mode (it could also be open as writable)
    module.write("MQ4, MQ5") # Writing the types of gases as headings in the file
    module.write("\n") # Writing a new line in the file
    print("MQ4, MQ5") # Displaying what was written to the file
    
while True: # Looping forever until a break is found
    with open(file, 'a') as module: # Reopening the file to add the values of the data readings in a comma separated format
        # Reading the values of all sensors and storing them in their respective variables
        mq4_value = mq4.read()
        mq5_value = mq5.read()

        # Printing the values of the sensors to the console
        print("{}, {}".format(mq4_value, mq5_value))
        # Writing the values of the sensors to the file
        module.write("{}, {}".format(mq4_value, mq5_value))
        # Writing the values of the sensors to the file
        module.write('\n') # Creating a breakline in the file after every write
    time.sleep(1)

