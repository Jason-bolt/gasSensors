 // Sensors Combined here
// MQ-5 
// MQ-4
// CCS811
// CJMCU-6814
// SHT30

#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"

bool enableHeater = false;
uint8_t loopCnt = 0;

Adafruit_SHT31 sht31 = Adafruit_SHT31();

unsigned long lastMillis = 0;


#include <Arduino.h>
#include <Wire.h>
#include "ccs811.h"  // CCS811 library

// nWAKE not controlled via Arduino host, so connect CCS811.nWAKE to GND
CCS811 ccs811; 

int sensor = 16;
//  Diameter of the wind vane in mm
int vane_diameter = 120;

//  Calculating the vane circumference
float vane_circ = ((vane_diameter * 1.000) / 1000) * 3.1415;

//  Vane inefficiency factor (Should come from a comparison with a working vane)
float err = 700.5;

// Defining defaults
int rotations = 0;
int trigger = 0;
int count = 0;
int sensorValue = 0;
float rots_per_second;
float windspeed;
bool label = true;

const int R_0 = 945; //Change this to your own R0 measurements

// the setup routine runs once when you press reset:
void setup() {

  
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
//  Cayenne.begin(username, password, clientID, ssid, wifiPassword);
  pinMode(sensor, INPUT);
  Serial.println("Starting measuring");

  // Enable I2C
  Wire.begin(); 
  
  // Enable CCS811
  ccs811.set_i2cdelay(50); // Needed for ESP8266 because it doesn't handle I2C clock stretch correctly
  bool ok= ccs811.begin();
  if( !ok ) Serial.println("setup: CCS811 begin FAILED");

  // Start measuring
  ok= ccs811.start(CCS811_MODE_1SEC);
  if( !ok ) Serial.println("setup: CCS811 start FAILED");

  while (!Serial)
    delay(10);     // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("SHT31 test");
  if (! sht31.begin(0x44)) {   // Set to 0x45 for alternate i2c addr
    Serial.println("Couldn't find SHT31");
    while (1) delay(1);
  }

  Serial.print("Heater Enabled State: ");
  if (sht31.isHeaterEnabled())
    Serial.println("ENABLED");
  else
    Serial.println("DISABLED");

}




// the loop routine runs over and over again forever:
void loop() {
//  Cayenne.loop();

  if (label){
    Serial.print("Timestamp");
    Serial.print(",");
    Serial.print("ECO2 (ppm)");
    Serial.print(",");
    Serial.print("ETVOC (ppb)");
    Serial.print(",");
//    Serial.print("O2");
//    Serial.print(",");
    Serial.print("Hydrogen");
    Serial.print(",");
    Serial.print("Methane");
    Serial.print(",");
    Serial.print("NO2");
    Serial.print(",");
    Serial.print("NH3");
    Serial.print(",");
    Serial.print("CO");
    Serial.print(",");
    Serial.print("Windspeed");
    Serial.print(",");
    Serial.print("Temperature");
    Serial.print(",");
    Serial.println("Humidity");
    label = false;
  }

  Serial.print(",");
  uint16_t eco2, etvoc, errstat, raw;
  ccs811.read(&eco2,&etvoc,&errstat,&raw); 
  
  // Print measurement results based on status
  if( errstat==CCS811_ERRSTAT_OK ) { 
//    Serial.print("CCS811: ");
//    Serial.print("eco2=");
    Serial.print(eco2);
    Serial.print(",");
//    Serial.print(" ppm  ");
//    Serial.print("etvoc=");
    Serial.print(etvoc);
    Serial.print(",");
//    Serial.print(" ppb  ");
    //Serial.print("raw6=");  Serial.print(raw/1024); Serial.print(" uA  "); 
    //Serial.print("raw10="); Serial.print(raw%1024); Serial.print(" ADC  ");
    //Serial.print("R="); Serial.print((1650*1000L/1023)*(raw%1024)/(raw/1024)); Serial.print(" ohm");
//    Serial.println();
//    Cayenne.virtualWrite(0, eco2);
//    Cayenne.virtualWrite(1, etvoc);
//    
  } else if( errstat==CCS811_ERRSTAT_OK_NODATA ) {
//    Serial.println("CCS811: waiting for (new) data");
      Serial.print("ECO2");
      Serial.print(",");
      Serial.print("ETVOC");
      Serial.print(",");
  } else if( errstat & CCS811_ERRSTAT_I2CFAIL ) { 
//    Serial.println("CCS811: I2C error");
      Serial.print("ECO2");
      Serial.print(",");
      Serial.print("ETVOC");
      Serial.print(",");
  } else {
//    Serial.print("CCS811: errstat=");
//    Serial.print(errstat,HEX); 
//    Serial.print("=");
//    Serial.println( ccs811.errstat_str(errstat) ); 
      Serial.print("ECO2");
      Serial.print(",");
      Serial.print("ETVOC");
      Serial.print(",");
  }

  // read the input on analog pin 0:
//  int o2 = analogRead(A1);
  // print out the value you read:
//  Serial.print("O2 = ");
//  Serial.print(o2);
//  Serial.print(",");
//  Cayenne.virtualWrite(2, o2);

  int mq5SensorValue = analogRead(27);
  // print out the value you read:
//  Serial.print("Hydrogen: ");
  Serial.print(mq5SensorValue);
  Serial.print(",");
//  Cayenne.virtualWrite(3, mq5SensorValue);

  int mq4SensorValue = analogRead(14);
  // print out the value you read:
//  Serial.print("Methane: ");
  Serial.print(mq4SensorValue);
  Serial.print(",");
//  Cayenne.virtualWrite(4, mq4SensorValue);

  // read the input on analog pin 0:
  int no2 = analogRead(35);
  int nh3 = analogRead(34);
  int co = analogRead(36);
  // print out the value you read:
//  Serial.print("NO2 = ");
  Serial.print(no2);
  Serial.print(",");
//  Cayenne.virtualWrite(5, no2);

//  Serial.print("NH3 = ");
  Serial.print(nh3);
  Serial.print(",");
//  Cayenne.virtualWrite(6, nh3);

//  Serial.print("CO = ");
  Serial.print(co);
  Serial.print(",");
//  Cayenne.virtualWrite(7, co);

  while (count < 6000){
    sensorValue = digitalRead(sensor);
//    Serial.println(sensorValue);
    if (sensorValue == 1 && trigger == 0){
      rotations = rotations + 1;
      trigger = 1;
    }
    if (sensorValue == 0){
      trigger = 0;
    }

//    Serial.println(rotations);

    count = count + 1;
    delay(1);
  }
  if (rotations == 1 && sensorValue == 1){
    rotations = 0;
  }
  rots_per_second = (rotations * 1.000) / 6000;
  windspeed = rots_per_second * vane_circ * err;
//  Serial.print("Windspeed is ");
  Serial.print(windspeed, 5);
  Serial.print(",");
//  Serial.println(" m/s");

  count = 0;
  rotations = 0;

  float t = sht31.readTemperature();
  float h = sht31.readHumidity();

  if (! isnan(t)) {  // check if 'is not a number'
//    Serial.print("Temp *C = ");
    Serial.print(t);
    Serial.print(",");
//    Serial.print("\t\t");
  } else { 
    Serial.println("Failed to read temperature");
  }
  
  if (! isnan(h)) {  // check if 'is not a number'
//    Serial.print("Hum. % = ");
    Serial.println(h);
  } else { 
//    Serial.println("Failed to read humidity");
  }

  delay(1000);

  // Toggle heater enabled state every 30 seconds
  // An ~3.0 degC temperature increase can be noted when heater is enabled
  if (++loopCnt == 30) {
    enableHeater = !enableHeater;
    sht31.heater(enableHeater);
    Serial.print("Heater Enabled State: ");
    if (sht31.isHeaterEnabled())
      Serial.println("ENABLED");
    else
      Serial.println("DISABLED");

    loopCnt = 0;
  }


  delay(500);        // delay in between reads for stability
}


//float getMethanePPM() {
//  float a2 = analogRead(A2); // get raw reading from sensor
//  float v_o = a2 * 5 / 1023; // convert reading to volts
//  float R_S = (5 - v_o) * 1000 / v_o; // apply formula for getting RS
//  float PPM = pow(R_S / R_0, -2.95) * 1000; //apply formula for getting PPM
//  return PPM; // return PPM value to calling function
//}
