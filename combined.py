from machine import Pin, ADC, I2C, SPI
import time
from CCS811 import CCS811
import sdcard
import os
from sht3x import SHT3X
import network
import socket
import gc
import uasyncio as asyncio



gc.collect()

ssid="fullSetup1"
password = "password1"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
    pass

print("Connection successful")
print(ap.ifconfig())


def web_page():
    html = """
            <!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
            rel="stylesheet"
            integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC"
            crossorigin="anonymous"
        />
        <title>Chart</title>
    </head>
    <body class="bg-warning p-5">
        <div class="col-md-6 offset-md-3">
            <div class="card">
                <div class="card-body">
                    <h1>
                        Gases chart
                        <button class="btn btn-success" onclick="updateChart()">
                            Update
                        </button>
                    </h1>
                    <canvas id="myChart"></canvas>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

        <script>
            // Array of current gas values in the SD card
            var mq4_1 = [0, 10, 5, 2, 20, 30, 45];
            var mq4_2 = [10, 20, 15, 12, 25, 39, 55];
            var mq5_1 = [11, 0, 1, 72, 55, 69, 35];
            var mq5_2 = [1, 30, 55, 112, 215, 379, 50];

            // Array of timestamps
            const labels = ["January", "February", "March", "April", "May", "June"];

            // Creating the datasets
            const data = {
                labels: labels,
                datasets: [
                    {
                        label: "First MQ4",
                        backgroundColor: "rgb(255, 0, 132)",
                        borderColor: "rgb(255, 0, 132)",
                        data: mq4_1,
                    },
                    {
                        label: "Second MQ4",
                        backgroundColor: "rgb(0, 99, 132)",
                        borderColor: "rgb(0, 99, 132)",
                        data: mq4_2,
                    },
                    {
                        label: "First MQ5",
                        backgroundColor: "rgb(255, 99, 132)",
                        borderColor: "rgb(255, 99, 132)",
                        data: mq5_1,
                    },
                    {
                        label: "Second MQ5",
                        backgroundColor: "rgb(0, 99, 0)",
                        borderColor: "rgb(0, 99, 0)",
                        data: mq5_2,
                        fill: false,
                    },
                ],
            };

            const config = {
                type: "line",
                data: data,
                options: {},
            };
        </script>

        <script>
            const myChart = new Chart(document.getElementById("myChart"), config);

            function updateChart() {
                myChart.data.labels.push("new");
                myChart.data.datasets[0].data = mq5_1;
                myChart.data.datasets[1].data = mq5_2;
                myChart.update();
            }
        </script>
    </body>
</html>

"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)


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

# CCS811
i2c = I2C(1, sda=Pin(21), scl=Pin(22))
ccs811 = CCS811(i2c)
time.sleep(1)

# CJMCU-6814
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


# for i in range(1, 61):
#     print(i)
#     time.sleep(1)

try:
    print("starting...")
    with open(file, 'w') as gasDataFile:
        gasDataFile.write("eCO2, TVOC, CO, NH3, NO2, Hydrogen(MQ5), Methane(MQ4), Humidity, Temperature, Wind speed")
        gasDataFile.write("\n")
        print("eCO2, TVOC, CO, NH3, NO2, Hydrogen(MQ5), Methane(MQ4), Humidity, Temperature, Wind speed")
        while True:
            try:
                if ccs811.data_ready():
#                     print('eCO2: %d ppm, TVOC: %d ppb' % (s.eCO2, s.tVOC))
                    co2Value = str(ccs811.eCO2)
                    tvocValue = str(ccs811.tVOC)
                    coValue = co.read()
                    nh3Value = nh3.read()
                    no2Value = no2.read()
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
                    
#                     time.sleep(1)
                    conn, addr = async s.accept()
#                     print('Got a connection from %s' %str(addr))
#                     
#                     request = conn.recv(1024)
#                     print('Content = %s' % str(request))
                    
#                     update = request.find('/?LED=1')
#                     led_off = request.find('/?LED=0')
#                     if led_on == 6:
#                         print("LED ON")
#                         print(str(led_on))
#                         led.value(1)
# 
#                     
#                     response = web_page()
#                     conn.send(response)
#                     conn.close()
            except OSError:
                print("OSError")
                continue
            time.sleep(1)
            gasDataFile.write("\n")
except KeyboardInterrupt:
    print("Ending...")