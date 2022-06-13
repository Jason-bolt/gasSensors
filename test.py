from machine import Pin, ADC, I2C, SPI
import time
from CCS811 import CCS811
import sdcard
import os
from sht3x import SHT3X


fileName = 'gasData'

count = 1
constFileName = 'gasData'
while True:
    if fileName + '.csv' in os.listdir('/'):
        fileName = constFileName + str(count)
    else:
        file = "/" + fileName + ".csv"
        break
    count += 1

i2c = I2C(1, sda=Pin(21), scl=Pin(22))
ccs811 = CCS811(i2c)
time.sleep(1)

co = ADC(Pin(36))
nh3 = ADC(Pin(34))
no2 = ADC(Pin(35))
windSpeedPin = Pin(16, Pin.IN)
windSpeed = 0.0
hydrogen = ADC(Pin(33))
methane = ADC(Pin(32))


def measure(i2c):  
    i2c.writeto(0x44, b'\x2C\x10')
    data = i2c.readfrom(0x44, 6) 
    
    aux = (data[0] << 8 | data[1]) * 175
    t_int = (aux // 0xffff) - 45;
    t_dec = (aux % 0xffff * 100) // 0xffff
    aux = (data[3] << 8 | data[4]) * 100
    h_int = aux // 0xffff
    h_dec = (aux % 0xffff * 100) // 0xffff
    return t_int, t_dec, h_int, h_dec


def mapValue(analogValue, actualLow, actualHigh, myLow, myHigh):
    if analogValue == 0:
        return myLow
    else:
        value = analogValue / actualHigh
        value = value * myHigh
        return value

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

    while (count < 6000):
        sensorValue = windSpeedPin.value()
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


try:
    print("starting...")
    with open(file, 'a') as gasDataFile:
        gasDataFile.write("eCO2, TVOC, CO, NH3, NO2, Hydrogen(MQ5), Methane(MQ4), Humidity, Temperature, Wind speed")
        gasDataFile.write("\n")
        print("eCO2, TVOC, CO, NH3, NO2, Hydrogen(MQ5), Methane(MQ4), Humidity, Temperature, Wind speed")
    while True:
        try:
            with open(file, 'a') as gasDataFile:    
                if ccs811.data_ready():
#                     print('eCO2: %d ppm, TVOC: %d ppb' % (s.eCO2, s.tVOC))
                    coValue = co.read()
                    nh3Value = nh3.read()
                    no2Value = no2.read()
                    co2Value = str(ccs811.eCO2)
                    tvocValue = str(ccs811.tVOC)
                    hydrogenValue = hydrogen.read()
                    methaneValue = methane.read()
                    measurement = measure(i2c)
                    temp = str(measurement[0]) + '.' + str(measurement[1])
                    humid = str(measurement[2]) + '.' + str(measurement[3])
                    windSpeed = calcWind()
                    print("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(co2Value, tvocValue, coValue, nh3Value, no2Value, hydrogenValue, methaneValue, temp, humid, windSpeed))
                    
                    values = str(co2Value)+','+str(tvocValue)+','+str(coValue)+','+str(nh3Value)+','+str(no2Value)+','+str(hydrogenValue)+','+str(methaneValue)+','+str(temp)+','+str(humid)+','+str(windSpeed)
                    gasDataFile.write(values)
                    
            #         CJMCU-6814
#                     coValue = mapValue(co.read(), 0, 4095, 1, 1000)
#                     nh3Value = mapValue(nh3.read(), 0, 4095, 1, 500)
#                     no2Value = mapValue(no2.read(), 0, 4095, 5, 1000)
                    gasDataFile.write("\n")
                   
        except OSError:
            print("OSError")
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Ending...")

